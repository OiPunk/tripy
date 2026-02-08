import uuid

from fastapi.testclient import TestClient

from tripy.app import create_app


def test_admin_endpoint_requires_permission() -> None:
    app = create_app()
    user_name = f"traveler_{uuid.uuid4().hex[:10]}"

    with TestClient(app) as client:
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "username": user_name,
                "password": "StrongPass123!",
                "real_name": "Traveler",
            },
        )
        assert register_response.status_code == 201

        traveler_login = client.post(
            "/api/v1/auth/login",
            json={"username": user_name, "password": "StrongPass123!"},
        )
        assert traveler_login.status_code == 200
        traveler_token = traveler_login.json()["access_token"]

        forbidden_response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {traveler_token}"},
        )
        assert forbidden_response.status_code == 403

        admin_login = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "ChangeMe123!"},
        )
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["access_token"]

        admin_response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert admin_response.status_code == 200
        assert isinstance(admin_response.json(), list)
