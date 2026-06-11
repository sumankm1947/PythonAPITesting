# Actual test cases

# 4 for get request
# 1 for post request
# 1 for patch request
# 1 for put request
# 1 for delete request
import pytest
import logging
from jsonschema import validate

from utils.api_client import APIClient
from utils.data_loader import load_schema, load_data

logger = logging.getLogger(__name__)

class TestPlaceholder:

    @pytest.mark.regression
    @pytest.mark.parametrize(
        "case",
        load_data("post_cases"),
        ids=lambda c: f"post{c['post_id']}-status{c['expected_status']}",
    )
    def test_get_post_cases(self, api_client_jsonplaceholder: APIClient, case: dict):
        response = api_client_jsonplaceholder.get(f"/posts/{case['post_id']}")

        assert response.status_code == case["expected_status"]

        if case["expected_status"] == 200:
            validate(response.json(), load_schema("post_jsonplaceholder"))
            assert response.json()["userId"] == case["expected_user"]

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_get_post(self, api_client_jsonplaceholder: APIClient):
        response = api_client_jsonplaceholder.get("/posts/1")

        assert response.status_code == 200
        validate(response.json(), load_schema("post_jsonplaceholder"))

        assert response.json()["userId"] == 1
        assert response.json()["id"] == 1

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_post_post(self, api_client_jsonplaceholder: APIClient):
        body_data = {
            "title": "foo",
            "body": "bar",
            "userId": 1,
        }
        response = api_client_jsonplaceholder.post("/posts", body=body_data)

        assert response.status_code == 201
        validate(response.json(), load_schema("post_jsonplaceholder"))

        assert response.json()["userId"] == 1
        assert response.json()["id"] == 101
        assert response.json()["title"] == "foo"
        assert response.json()["body"] == "bar"
    
    @pytest.mark.regression
    def test_patch_post(self, api_client_jsonplaceholder: APIClient):
        body_data = {
            "title": "foo",
        }
        header_data = {
            "Content-type": "application/json; charset=UTF-8"
        }

        response = api_client_jsonplaceholder.patch("/posts/1", body=body_data, headers=header_data)

        assert response.status_code == 200
        validate(response.json(), load_schema("post_jsonplaceholder"))

        assert response.json()["userId"] == 1
        assert response.json()["id"] == 1
        assert response.json()["title"] == "foo"
    
    @pytest.mark.regression
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
        validate(response.json(), load_schema("post_jsonplaceholder"))

        assert response.json()["userId"] == 1
        assert response.json()["id"] == 1
        assert response.json()["title"] == "foo"
        assert response.json()["body"] == "bar"
    
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_delete_post(self, api_client_jsonplaceholder: APIClient):
        response = api_client_jsonplaceholder.delete("/posts/1")
        
        assert response.status_code == 200

