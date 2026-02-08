from fastapi.testclient import TestClient

from tripy.app import create_app


def test_liveness() -> None:
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/api/v1/health/live")
        assert response.status_code == 200
        assert "status" in response.json()


def test_readiness() -> None:
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/api/v1/health/ready")
        assert response.status_code == 200
        assert "status" in response.json()
