import pytest
import requests
import logging
from typing import Generator

from config.config import API_ENDPOINT_JSONPLACEHOLDER
from utils.api_client import APIClient

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