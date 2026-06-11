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
    def test_patch_partial_update(self, api_session_restfulbooker : APIClient, created_booking: str):
        bookingid = created_booking
        request_body = {
            "firstname" : "YoYo",
            "lastname" : "Mandal",
        }
        response = api_session_restfulbooker.patch(f"/booking/{bookingid}", body=request_body)

        assert response.status_code == 200
        assert response.json()["firstname"] == "YoYo"
        assert response.json()["lastname"] == "Mandal"

        response_for_get = api_session_restfulbooker.get(f"/booking/{bookingid}")
        
        assert response.status_code == 200
        assert response_for_get.json()["firstname"] == "YoYo"
        assert response_for_get.json()["lastname"] == "Mandal"




    @pytest.mark.auth
    def test_delete_booking_withouttoken(self, created_booking: str):
        client = APIClient(base_url=API_ENDPOINT_RESTFULBOOKER)
        response = client.delete(f"/booking/{created_booking}")

        assert response.status_code == 403


    @pytest.mark.auth
    def test_delete_booking(self, api_session_restfulbooker: APIClient, created_booking):
        bookingid = created_booking
        response = api_session_restfulbooker.delete(f"/booking/{bookingid}")

        assert response.status_code == 201
    
        response_for_get = api_session_restfulbooker.get(f"/booking/{bookingid}")
        
        assert response_for_get.status_code == 404
