import pytest
import requests
import logging
from typing import Generator
from pathlib import Path
import json

from config.config import API_ENDPOINT_JSONPLACEHOLDER, API_ENDPOINT_RESTFULBOOKER
from utils.api_client import APIClient

PROJECT_ROOT = Path(__file__).resolve().parent

logging.basicConfig(level=logging.INFO)

# demo fixture => not needed fixture anymore except the demo test case
@pytest.fixture
def base_url_jsonplaceholder():
    return API_ENDPOINT_JSONPLACEHOLDER

# demo fixture => not needed fixture anymore except the demo test case
@pytest.fixture(scope="session")
def api_session() -> Generator[requests.Session, None, None]:
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    yield session
    session.close()

@pytest.fixture
def api_client_jsonplaceholder():
    api_client = APIClient(base_url=API_ENDPOINT_JSONPLACEHOLDER)
    yield api_client
    api_client.session.close()


@pytest.fixture(scope="session")
def restful_booker_token():
    client = APIClient(base_url=API_ENDPOINT_RESTFULBOOKER)
    response = client.post("/auth", {
        "username" : "admin",
        "password" : "password123"
    })
    return response.json()["token"]


@pytest.fixture(scope="session")
def api_session_restfulbooker(restful_booker_token) -> Generator[requests.Session, None, None]:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Cookie": f"token={restful_booker_token}"
    }
    client = APIClient(base_url=API_ENDPOINT_RESTFULBOOKER, headers=headers)
    yield client

    client.session.close()

@pytest.fixture
def created_booking(api_session_restfulbooker, booking_payload):
    response = api_session_restfulbooker.post("/booking", booking_payload)
    return response.json()["bookingid"]


@pytest.fixture
def booking_payload():
    payloadpath = PROJECT_ROOT / "data" / "booking_payload.json"

    with open(payloadpath, "r", encoding="utf-8") as f:
        return json.load(f)
