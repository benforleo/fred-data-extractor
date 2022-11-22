import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from requests import HTTPError, RequestException
import requests.exceptions
from lambda_.fred_extractor import FredExtractor


class TestFredExtractor:
    @patch.object(FredExtractor, 'retrieve_api_key')
    @patch('lambda_.fred_extractor.requests')
    def test_request_fred_data_raises_exception_for_http_error(self, mock_requests, mock_fred_extractor, event_fixture):

        mock_requests.exceptions = requests.exceptions
        mock_response = Mock(status_code=403)
        mock_response.raise_for_status.side_effect = HTTPError('Something goes wrong')
        mock_requests.get.return_value = mock_response

        mock_fred_extractor.retrieve_api_key.return_value = '1234'
        fred = FredExtractor(event_fixture, None, None, None)

        with pytest.raises(RequestException):
            fred.request_fred_data()

    @patch.object(FredExtractor, 'retrieve_api_key')
    @patch('lambda_.fred_extractor.requests')
    def test_fred_extractor_state_change_with_successful_request(self, mock_requests, mock_fred_extractor, event_fixture):
        mock_response = Mock(status_code=200)
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'mock': 'data'}
        mock_requests.get.return_value = mock_response

        mock_fred_extractor.retrieve_api_key.return_value = '1234'
        fred = FredExtractor(event_fixture, None, None, None)

        fred.request_fred_data()
        assert fred.data == {'mock': 'data'}

    def test_generate_observation_date_returns_valid_datetime(self, event_fixture):
        observation_datetime = FredExtractor.generate_observation_date(event_fixture)
        assert isinstance(observation_datetime, datetime)
