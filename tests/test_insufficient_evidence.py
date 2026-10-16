from unittest.mock import patch

from app.agents.incident_agent import IncidentAgent


def test_insufficient_evidence():
    with (
        patch(
            "app.agents.incident_agent.KnowledgeBase.search",
            return_value=[],
        ),
        patch(
            "app.agents.incident_agent.EvidenceCollector.collect",
            return_value=[],
        ),
        patch(
            "app.agents.incident_agent.LLMService.analyze"
        ) as mock_analyze,
    ):
        agent = IncidentAgent()

        result = agent.analyze(
            "POST /unknown returns HTTP 500"
        )

        assert result["diagnosis"] == (
            "Insufficient evidence to determine the root cause."
        )
        assert result["confidence"] == 0.0
        assert result["evidence"] == []
        assert result["possible_causes"] == []
        mock_analyze.assert_not_called()


def test_irrelevant_evidence_does_not_trigger_diagnosis():
    irrelevant_evidence = [
        {
            "source": "docs/general.md",
            "chunk_id": "general-1",
            "content": "The application has a user profile endpoint.",
            "score": 0.95,
        }
    ]

    with (
        patch(
            "app.agents.incident_agent.KnowledgeBase.search",
            return_value=irrelevant_evidence,
        ),
        patch(
            "app.agents.incident_agent.EvidenceCollector.collect",
            return_value=[],
        ),
        patch(
            "app.agents.incident_agent.LLMService.analyze"
        ) as mock_analyze,
    ):
        agent = IncidentAgent()

        result = agent.analyze(
            "POST /unknown returns HTTP 500"
        )

        assert result["diagnosis"] == (
            "Insufficient evidence to determine the root cause."
        )
        assert result["confidence"] == 0.0
        assert result["evidence"] == []
        mock_analyze.assert_not_called()