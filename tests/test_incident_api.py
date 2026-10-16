from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_incident_analysis_endpoint():
    mock_result = {
        "incident": "POST /payment is returning HTTP 500",
        "diagnosis": "Database insertion failed because transaction_id was NULL.",
        "evidence": [],
        "confidence": 0.9,
        "possible_causes": [
            "The transaction_id field was missing."
        ],
        "recommended_actions": [
            "Validate transaction_id before inserting the payment."
        ],
        "verification_steps": [
            "Retry the request with a valid transaction_id."
        ],
    }

    with patch(
        "app.api.routes.incidents.analyze_incident",
        return_value=mock_result,
    ) as mock_analyze:
        response = client.post(
            "/incidents/analyze",
            json={
                "incident": "POST /payment is returning HTTP 500"
            },
        )

    assert response.status_code == 200
    assert response.json()["diagnosis"] == mock_result["diagnosis"]
    assert response.json()["confidence"] == 0.9
    mock_analyze.assert_called_once()

def test_incident_analysis_rejects_missing_incident():
    response = client.post(
        "/incidents/analyze",
        json={},
    )

    assert response.status_code == 422

def test_incident_analysis_rejects_empty_incident():
    response = client.post(
        "/incidents/analyze",
        json={"incident": ""},
    )

    assert response.status_code == 422