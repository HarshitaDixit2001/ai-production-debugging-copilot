from unittest.mock import patch

from app.agents.incident_agent import IncidentAgent


def test_agent_collects_evidence():
    mock_analysis = {
        "diagnosis": (
            "Database insertion failed because transaction_id was NULL."
        ),
        "evidence": [
            "DatabaseError: Cannot insert NULL into column transaction_id"
        ],
        "confidence": 0.95,
        "possible_causes": [
            "transaction_id was generated after database insertion"
        ],
        "recommended_actions": [
            "Generate transaction_id before inserting the payment record"
        ],
        "verification_steps": [
            "Retry POST /payment"
        ],
    }

    with patch(
        "app.agents.incident_agent.LLMService.analyze",
        return_value=mock_analysis,
    ):
        agent = IncidentAgent()

        result = agent.analyze(
            "POST /payment is returning HTTP 500"
        )

    assert result["diagnosis"]
    assert result["evidence"]
    assert result["confidence"] > 0
    assert result["recommended_actions"]