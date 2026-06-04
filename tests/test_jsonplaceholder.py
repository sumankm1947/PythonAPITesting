# Actual test cases

# 4 for get request
# 1 for post request
# 1 for patch request
# 1 for put request
# 1 for delete request

import logging

from utils.api_client import APIClient

logger = logging.getLogger(__name__)

class TestPlaceholder:

    def test_get_post(self, api_client_jsonplaceholder: APIClient):
        response = api_client_jsonplaceholder.get("/posts/1")

        assert response.status_code == 200
        assert response.json()["userId"] == 1
        assert response.json()["id"] == 1

    def test_post_post(self, api_client_jsonplaceholder: APIClient):
        body_data = {
            "title": "foo",
            "body": "bar",
            "userId": 1,
        }
        response = api_client_jsonplaceholder.post("/posts", body=body_data)

        assert response.status_code == 201
        assert response.json()["userId"] == 1
        assert response.json()["id"] == 101
        assert response.json()["title"] == "foo"
        assert response.json()["body"] == "bar"
    
    def test_patch_post(self, api_client_jsonplaceholder: APIClient):
        body_data = {
            "title": "foo",
        }
        header_data = {
            "Content-type": "application/json; charset=UTF-8"
        }

        response = api_client_jsonplaceholder.patch("/posts/1", body=body_data, headers=header_data)

        assert response.status_code == 200
        assert response.json()["userId"] == 1
        assert response.json()["id"] == 1
        assert response.json()["title"] == "foo"
    
    def test_put_post(self, api_client_jsonplaceholder: APIClient):
        body_data = {
            "id": 1,
            "title": "foo",
            "body": "bar",
            "userId": 1,
        }

        header_data = {
            "Content-type": "application/json; charset=UTF-8",
        }

        response = api_client_jsonplaceholder.put("/posts/1", body=body_data, headers=header_data)

        assert response.status_code == 200
        assert response.json()["userId"] == 1
        assert response.json()["id"] == 1
        assert response.json()["title"] == "foo"
        assert response.json()["body"] == "bar"
    
    def test_delete_post(self, api_client_jsonplaceholder: APIClient):
        response = api_client_jsonplaceholder.delete("/posts/1")
        
        assert response.status_code == 200

