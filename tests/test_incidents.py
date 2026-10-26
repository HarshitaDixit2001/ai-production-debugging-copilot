from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_analyze_incident():
    mock_evidence = [
        {
            "source": "error.log",
            "chunk_id": "error-001",
            "content": (
                "POST /payment failed. "
                "DatabaseError: Cannot insert NULL into column transaction_id"
            ),
            "score": 0.95,
        }
    ]

    mock_analysis = {
        "diagnosis": (
            "Database insertion failed because transaction_id was NULL."
        ),
        "evidence": ["error.log"],
        "confidence": 0.95,
        "possible_causes": [
            "transaction_id was generated after database insertion"
        ],
        "recommended_actions": [
            "Generate transaction_id before inserting the payment record"
        ],
        "verification_steps": [
            "Retry POST /payment and verify a transaction_id is persisted"
        ],
    }

    with (
        patch(
            "app.agents.incident_agent.KnowledgeBase.search",
            return_value=mock_evidence,
        ),
        patch(
            "app.agents.incident_agent.EvidenceCollector.collect",
            return_value=[],
        ),
        patch(
            "app.agents.incident_agent.LLMService.analyze",
            return_value=mock_analysis,
        ),
    ):
        response = client.post(
            "/incidents/analyze",
            json={
                "incident": "POST /payment is returning HTTP 500",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["incident"] == (
        "POST /payment is returning HTTP 500"
    )
    assert data["diagnosis"] == mock_analysis["diagnosis"]
    assert data["evidence"]
    assert data["evidence"][0]["source"] == "error.log"
    assert "transaction_id" in data["evidence"][0]["content"]
    assert data["confidence"] == 0.95