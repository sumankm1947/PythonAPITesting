import pytest

from utils.api_client import APIClient
from config.config import API_ENDPOINT_RESTFULBOOKER

class TestRestfulBooker:

    @pytest.mark.auth
    def test_post_createbooking(self, api_session_restfulbooker: APIClient, booking_payload: dict):

        response = api_session_restfulbooker.post("/booking", booking_payload)
        assert response.status_code == 200
        assert response.json()["booking"]["firstname"] == "Suman"
        assert response.json()["booking"]["lastname"] == "Mandal"


    @pytest.mark.auth
    def test_delete_booking_withouttoken(self, created_booking):
        client = APIClient(base_url=API_ENDPOINT_RESTFULBOOKER)
        response = client.delete(f"/booking/{created_booking}")

        assert response.status_code == 403