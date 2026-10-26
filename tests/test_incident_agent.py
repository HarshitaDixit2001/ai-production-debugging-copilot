from unittest.mock import patch

from app.agents.incident_agent import IncidentAgent


def test_agent_returns_valid_analysis():
    retrieved_evidence = [
        {
            "source": "data/logs/error.log",
            "chunk_id": "payment-error-1",
            "content": (
                "POST /payment returned HTTP 500. "
                "Database insertion failed because transaction_id was NULL."
            ),
            "score": 0.95,
        }
    ]

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

    with (
        patch(
            "app.agents.incident_agent.KnowledgeBase.search",
            return_value=retrieved_evidence,
        ),
        patch(
            "app.agents.incident_agent.EvidenceCollector.collect",
            return_value=[],
        ),
        patch(
            "app.agents.incident_agent.is_relevant_evidence",
            return_value=True,
        ),
        patch(
            "app.agents.incident_agent.LLMService.analyze",
            return_value=mock_analysis,
        ),
    ):
        agent = IncidentAgent()
        result = agent.analyze("POST /payment is returning HTTP 500")

    assert result["diagnosis"] == mock_analysis["diagnosis"]
    assert result["confidence"] == 0.9
    assert result["evidence"] == retrieved_evidence
    assert isinstance(result["possible_causes"], list)
    assert isinstance(result["recommended_actions"], list)
    assert isinstance(result["verification_steps"], list)

def test_unsupported_llm_citation_triggers_safe_abstention():
    retrieved_evidence = [
        {
            "source": "data/logs/error.log",
            "chunk_id": "payment-error-1",
            "content": (
                "POST /payment returned HTTP 500. "
                "Database insertion failed because transaction_id was NULL."
            ),
            "score": 0.95,
        }
    ]

    unsupported_analysis = {
        "diagnosis": "The database server is offline.",
        "evidence": ["The database server is offline."],
        "confidence": 0.95,
        "possible_causes": ["Database outage"],
        "recommended_actions": ["Restart the database"],
        "verification_steps": ["Check database availability"],
    }

    with (
        patch(
            "app.agents.incident_agent.KnowledgeBase.search",
            return_value=retrieved_evidence,
        ),
        patch(
            "app.agents.incident_agent.EvidenceCollector.collect",
            return_value=[],
        ),
        patch(
            "app.agents.incident_agent.is_relevant_evidence",
            return_value=True,
        ),
        patch(
            "app.agents.incident_agent.LLMService.analyze",
            return_value=unsupported_analysis,
        ),
    ):
        agent = IncidentAgent()
        result = agent.analyze(
            "POST /payment is returning HTTP 500"
        )

    assert result["diagnosis"] == (
        "Insufficient evidence to determine the root cause."
    )
    assert result["confidence"] == 0.0
    assert result["evidence"] == []
    assert result["possible_causes"] == []
