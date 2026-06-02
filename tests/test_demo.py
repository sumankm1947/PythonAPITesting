import logging

logger = logging.getLogger(__name__)

class TestDemo:    

    def test_get_post(self, base_url_jsonplaceholder, api_session):
        response = api_session.get(f"{base_url_jsonplaceholder}/posts/1")
        assert response.status_code == 200
        assert response.json()["userId"] == 1
        assert response.json()["id"] == 1
        logger.info(f"Response: {response.json()}")
    
    def test_post_post(self, base_url_jsonplaceholder, api_session):
        requests_data = {
            "title": "foo",
            "description": "bar",
            "userId": 1
        }

        response = api_session.post(f"{base_url_jsonplaceholder}/posts", json=requests_data)

        logger.info(f"Response: {response.json()}") 
        assert response.status_code == 201
        assert response.json()["userId"] == 1
        assert response.json()["id"] == 101
