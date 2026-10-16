from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_request_id_is_generated_when_missing():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")


def test_valid_request_id_is_preserved():
    request_id = "incident-test-123"

    response = client.get(
        "/health",
        headers={"X-Request-ID": request_id},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id


def test_invalid_request_id_is_replaced():
    response = client.get(
        "/health",
        headers={"X-Request-ID": "invalid request id"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] != "invalid request id"
    assert " " not in response.headers["X-Request-ID"]