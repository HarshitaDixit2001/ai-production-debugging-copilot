from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app, raise_server_exceptions=False)


def test_global_exception_handler():
    with patch(
        "app.services.incident_service.agent.analyze",
        side_effect=RuntimeError("Unexpected failure"),
    ):
        response = client.post(
            "/incidents/analyze",
            json={
                "incident": "POST /payment is returning HTTP 500",
            },
        )

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"
    assert response.json()["request_id"]
    assert response.headers["X-Request-ID"] == response.json()["request_id"]
    assert "Unexpected failure" not in response.text