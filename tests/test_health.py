from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch("app.main.Client")
def test_readiness_endpoint_when_model_is_available(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_client.show.return_value = {"model": "qwen3:8b"}

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["model"]


@patch("app.main.Client")
def test_readiness_endpoint_when_model_is_unavailable(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_client.show.side_effect = Exception("Ollama unavailable")

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
