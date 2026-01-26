import json
import pytest
from tests.data.secret_response import secret_response


@pytest.fixture
def event_fixture():
    with open("./tests/data/event.json", "r") as file:
        event = json.load(file)
    return event

@pytest.fixture
def api_response_fixture():
    with open("./tests/data/response.json", "r") as file:
        response = json.load(file)
    return response


@pytest.fixture
def secret_response_fixture():
    return secret_response
