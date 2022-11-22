import json
import pytest


@pytest.fixture
def event_fixture():
    with open("./tests/data/event.json", "r") as file:
        event = json.load(file)
    return event
