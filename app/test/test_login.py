from fastapi.testclient import TestClient
from app.main import app
from app.settings import Settings
import requests

client = TestClient(app)
settings = Settings()


def get_jwt_token():
    """
    Get a valid JWT token from keycloak
    :return:
    """
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = f"client_id={settings.keycloak_client_id}" \
           f"&username={settings.keycloak_username_test}" \
           f"&password={settings.keycloak_password_test}" \
           f"&grant_type=password"

    r = requests.post(headers=headers, data=data, url=settings.keycloak_token_url)
    return r.json()["access_token"]


def test_request_without_auth():
    response = client.get('/ping')
    assert response.status_code == 401
    assert response.json() == {'detail': "User is not correctly authentified"}


def test_request_with_auth():
    token = get_jwt_token()
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = client.get('/ping', headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}





