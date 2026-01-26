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
