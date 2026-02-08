import uuid

from fastapi.testclient import TestClient

from tripy.app import create_app


def test_register_login_and_me_flow() -> None:
    app = create_app()
    username = f"user_{uuid.uuid4().hex[:10]}"

    with TestClient(app) as client:
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "password": "StrongPass123!",
                "real_name": "Test User",
            },
        )
        assert register_response.status_code == 201

        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": username, "password": "StrongPass123!"},
        )
        assert login_response.status_code == 200
        payload = login_response.json()
        token = payload["access_token"]
        assert "traveler" in payload["roles"]
        assert "graph:execute" in payload["permissions"]

        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_response.status_code == 200
        assert me_response.json()["username"] == username
        assert "traveler" in me_response.json()["roles"]
