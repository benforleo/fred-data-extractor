import boto3.session
import pendulum
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from requests import HTTPError, RequestException
import requests.exceptions
from botocore.stub import Stubber
from src.fred_extractor.fred_extractor import FredExtractor


class TestFredExtractor:

    def test_request_fred_data_returns_valid_response(self, event_fixture, api_response_fixture):
        fred = FredExtractor(
            event_fixture,
            None,
            None,
            "bucket",
        )

        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = api_response_fixture
            mock_get.return_value = mock_response
            result = fred.request_fred_data('secret-value')
            assert result == api_response_fixture
            assert 'observations' in result
            assert len(result['observations']) == 1

    def test_request_fred_data_calls_api_with_correct_parameters(self, event_fixture):
        fred = FredExtractor(event_fixture, None, None, "bucket")

        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"observations": []}
            mock_get.return_value = mock_response

            fred.request_fred_data("test-api-key")

            mock_get.assert_called_once_with(url=FredExtractor.API_URL, timeout=FredExtractor.API_TIMEOUT, params={
                "series_id": fred.series_id,
                "frequency": "d",
                "observation_start": fred.observation_date.format("YYYY-MM-DD"),
                "observation_end": fred.observation_date.format("YYYY-MM-DD"),
                "api_key": "test-api-key",
                "file_type": "json",
            })

    def test_request_fred_data_uses_custom_series_id(self, event_fixture):
        fred = FredExtractor(event_fixture, None, None, "bucket", series_id="DGS10")

        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"observations": []}
            mock_get.return_value = mock_response

            fred.request_fred_data("test-api-key")

            assert mock_get.call_args.kwargs['params']['series_id'] == "DGS10"

    def test_request_fred_data_raises_http_error_on_4xx(self, event_fixture):
        fred = FredExtractor(event_fixture, None, None, "bucket")

        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = HTTPError(response=Mock(status_code=400))
            mock_get.return_value = mock_response

            with pytest.raises(HTTPError):
                fred.request_fred_data("invalid-key")

    def test_generate_s3_object_key_returns_correct_string(self, event_fixture):
        fred = FredExtractor(
            event_fixture,
            None,
            None,
            "bucket",
        )
        key = fred.generate_s3_object_key()
        assert key == "fred/SP500/year=2022/month=07/SP500-2022-07-21.json"

    def test_observation_date_caches_the_correct_date(self, event_fixture):
        fred = FredExtractor(
            event_fixture,
            None,
            None,
            "bucket",
        )
        observation_date = fred.observation_date
        assert observation_date == pendulum.parse("2022-07-21T00:00:00Z")

    def test_observation_date_caches_result_across_multiple_calls(self, event_fixture):
        fred = FredExtractor(event_fixture, None, None, "bucket")

        first_call = fred.observation_date
        second_call = fred.observation_date

        assert first_call is second_call
        assert first_call == pendulum.parse("2022-07-21T00:00:00Z")

    def test__validate_event_raises_exception_for_missing_time_key(self):
        with pytest.raises(ValueError, match="Event must contain 'time' field"):
            FredExtractor._validate_event({})
