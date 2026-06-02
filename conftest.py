import pytest
import requests
import logging

from config.config import API_ENDPOINT_JSONPLACEHOLDER

logging.basicConfig(level=logging.INFO)

@pytest.fixture
def base_url_jsonplaceholder():
    return API_ENDPOINT_JSONPLACEHOLDER

@pytest.fixture(scope="session")
def api_session():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})

    yield session
    session.close()