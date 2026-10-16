from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.services.incident_service.agent")
def test_rejects_incident_that_is_too_short(mock_agent):
    response = client.post(
        "/incidents/analyze",
        json={"incident": "bad"},
    )

    assert response.status_code == 422
    mock_agent.analyze.assert_not_called()

def test_rejects_incident_that_is_too_long():
    response = client.post(
        "/incidents/analyze",
        json={"incident": "A" * 2001},
    )

    assert response.status_code == 422


@patch("app.services.incident_service.agent")
def test_accepts_incident_with_valid_length(mock_agent):
    mock_agent.analyze.return_value = {
        "diagnosis": "Test diagnosis",
        "evidence": [
            {
                "source": "test.log",
                "content": "Test evidence",
                "score": 0.8,
            }
        ],
        "confidence": 0.8,
        "possible_causes": ["Test cause"],
        "recommended_actions": ["Test action"],
        "verification_steps": ["Test verification"],
    }

    response = client.post(
        "/incidents/analyze",
        json={"incident": "Payment API returns HTTP 500"},
    )

    assert response.status_code == 200
    mock_agent.analyze.assert_called_once()
