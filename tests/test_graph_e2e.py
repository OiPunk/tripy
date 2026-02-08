from __future__ import annotations

from fastapi.testclient import TestClient

from tripy.api.v1.endpoints import graph as graph_endpoint
from tripy.app import create_app


class AIMessage:
    def __init__(self, content: str):
        self.content = content


class _FakeState:
    def __init__(self, has_next: bool):
        self.next = ["pending"] if has_next else []


class _FakeGraph:
    def stream(self, payload, config, stream_mode="values"):
        if payload is None:
            return [{"messages": [AIMessage("Action completed")]}]
        return [{"messages": [AIMessage("Preparing a booking action")]}]

    def get_state(self, config):
        thread_id = config["configurable"]["thread_id"]
        return _FakeState(thread_id.endswith("-interrupt"))


def test_graph_execution_flow_with_interrupt(monkeypatch) -> None:
    fake_graph = _FakeGraph()
    monkeypatch.setattr(graph_endpoint.service, "_get_graph", lambda: fake_graph)

    app = create_app()
    with TestClient(app) as client:
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "ChangeMe123!"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        first_response = client.post(
            "/api/v1/graph/execute",
            json={"user_input": "book a hotel", "thread_id": "test-interrupt"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert first_response.status_code == 200
        assert first_response.json()["interrupted"] is True

        second_response = client.post(
            "/api/v1/graph/execute",
            json={"user_input": "y", "thread_id": "test-confirm"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert second_response.status_code == 200
        assert second_response.json()["interrupted"] is False
        assert second_response.json()["assistant"] == "Action completed"
