import requests
import logging

class TestDemo:
    BASE_URL = "https://jsonplaceholder.typicode.com"
    
    def test_get_post(self):
        response = requests.get(f"{self.BASE_URL}/posts/1")
        assert response.status_code == 200
        assert response.json()["userId"] == 1
        assert response.json()["id"] == 1
        # print(response.json())
    
    def test_post_post(self):
        requests_data = {
            "title": "foo",
            "description": "bar",
            "userId": 1
        }

        reponse = requests.post(f"{self.BASE_URL}/posts", requests_data)

        assert reponse.status_code == 201
        # print(reponse.json())
        
        assert reponse.json()["userId"] == '1'
        assert reponse.json()["id"] == 101
