import boto3.session
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from requests import HTTPError, RequestException
import requests.exceptions
from botocore.stub import Stubber
from lambda_.fred_extractor.fred_extractor import FredExtractor


class TestFredExtractor:

    @patch('lambda_.fred_extractor.fred_extractor.requests', spec=True)
    def test_request_fred_data_raises_exception_for_http_error(self, mock_requests, event_fixture):
        # Mock the response object to the get request
        mock_response = Mock(status_code=403)
        mock_response.raise_for_status.side_effect = HTTPError('Something goes wrong')

        # Mock the requests module itself, returning our mock response from the get call
        mock_requests.exceptions = requests.exceptions
        mock_requests.get.return_value = mock_response

        fred = FredExtractor(event_fixture, None, None, None)

        with pytest.raises(RequestException):
            fred.request_fred_data(api_key="fake-api-key")

    @patch('lambda_.fred_extractor.fred_extractor.requests')
    def test_request_fred_data_arguments(self, mock_requests, event_fixture):

        # Stub the response from requests.get
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = "Fake response"

        mock_requests.get.return_value = mock_response

        fred = FredExtractor(event_fixture, None, None, None)
        fred.request_fred_data(api_key="fake-api-key")

        mock_requests.get.assert_called_once()
        mock_requests.get.assert_called_with(
            url="https://api.stlouisfed.org/fred/series/observations",
            params={
                'series_id': 'SP500',
                'frequency': 'd',
                'observation_start': '2022-07-21',  # - 1 day from fixture event time
                'observation_end': '2022-07-21',
                'api_key': 'fake-api-key',
                'file_type': 'json'
            }
        )

    def test_retrieve_api_key_returns_correct_secret_key(self, event_fixture, secret_response_fixture):
        mock_session = Mock()

        client = boto3.session.Session().client(service_name='secretsmanager', region_name='us-east-1')
        mock_session.client.return_value = client

        # stub the S3 client with secret_response fixture
        secrets_stubber = Stubber(client)
        secrets_stubber.add_response('get_secret_value', secret_response_fixture)

        with secrets_stubber:
            fred = FredExtractor(event_fixture, None, mock_session, 'fake-bucket')
            api_key = fred.retrieve_api_key()

        assert api_key == 'super-secret-key'

    def test_retrieve_api_key_makes_boto3_calls_with_correct_arguments(self, event_fixture):
        mock_session = Mock()
        mock_client = Mock()

        mock_session.client.return_value = mock_client
        mock_client.get_secret_value.return_value = {'SecretString': '{"fred-api-key": "fake-secret"}'}

        fred = FredExtractor(event_fixture, None, mock_session, 'fake-bucket')
        fred.retrieve_api_key()

        mock_session.client.assert_called_once_with(service_name='secretsmanager')
        mock_client.get_secret_value.assert_called_once_with(SecretId="dev/FredExtractor/APIKey")

    def test_generate_s3_object_key_produces_desired_s3_path(self):
        fred = FredExtractor(None, None, None, None)
        fake_datetime = datetime(2022, 1, 1)
        fred.observation_date = fake_datetime
        fred.series_id = 'SP500'

        key = fred.generate_s3_object_key()
        assert key == "fred/SP500/year=2022/month=01/SP500-2022-01-01.json"

    def test_generate_observation_date_returns_valid_datetime(self, event_fixture):
        observation_datetime = FredExtractor.generate_observation_date(event_fixture)
        assert isinstance(observation_datetime, datetime)
        assert observation_datetime == datetime(2022, 7, 21)
