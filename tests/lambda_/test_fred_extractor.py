import json
import pytest
from datetime import datetime
from lambda_.fred_extractor import FredExtractor


@pytest.fixture
def event_fixture():
    with open("./tests/data/event.json", "r") as file:
        event = json.load(file)
    return event


def test_generate_observation_date_returns_valid_datetime(event_fixture):
    observation_datetime = FredExtractor.generate_observation_date(event_fixture)
    assert isinstance(observation_datetime, datetime)
