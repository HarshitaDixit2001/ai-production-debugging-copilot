from unittest.mock import patch

from app.models.incident import IncidentRequest
from app.services.incident_service import analyze_incident


def test_analyze_incident_normalizes_string_evidence():
    mock_analysis = {
        "diagnosis": "Database insertion failed because transaction_id was NULL.",
        "evidence": [
            "DatabaseError: Cannot insert NULL into transaction_id",
            "PaymentService.create_payment failed",
        ],
        "confidence": 0.9,
        "possible_causes": ["Missing transaction_id during insertion"],
        "recommended_actions": ["Validate transaction_id before database insertion"],
        "verification_steps": ["Retry the payment and verify the database record"],
    }

    with patch(
        "app.services.incident_service.agent.analyze",
        return_value=mock_analysis,
    ):
        result = analyze_incident(
            IncidentRequest(
                incident="POST /payment is returning HTTP 500"
            )
        )

    assert result.diagnosis == mock_analysis["diagnosis"]
    assert len(result.evidence) == 2
    assert all(isinstance(item, dict) for item in result.evidence)
    assert result.evidence[0]["content"].startswith("DatabaseError")
    assert result.evidence[0]["source"] == "AI analysis"
    assert 0.0 <= result.confidence <= 1.0