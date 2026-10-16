from unittest.mock import patch

from app.agents.incident_agent import IncidentAgent


def test_agent_returns_valid_analysis():
    mock_analysis = {
        "diagnosis": "Database insertion failed because transaction_id was NULL.",
        "evidence": ["data/logs/error.log"],
        "confidence": 0.9,
        "possible_causes": [
            "The transaction_id field was missing from the request."
        ],
        "recommended_actions": [
            "Validate transaction_id before inserting the payment."
        ],
        "verification_steps": [
            "Reproduce the request and confirm transaction_id is present."
        ],
    }

    with patch(
        "app.agents.incident_agent.LLMService.analyze",
        return_value=mock_analysis,
    ):
        agent = IncidentAgent()
        result = agent.analyze("POST /payment is returning HTTP 500")

    assert result["diagnosis"] == mock_analysis["diagnosis"]
    assert result["confidence"] == 0.9
    assert isinstance(result["evidence"], list)
    assert isinstance(result["possible_causes"], list)
    assert isinstance(result["recommended_actions"], list)
    assert isinstance(result["verification_steps"], list)