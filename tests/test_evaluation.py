
import json
from pathlib import Path
from unittest.mock import patch

from app.agents.incident_agent import IncidentAgent


def test_evaluation_dataset():
    dataset_path = Path("evaluation/dataset.json")

    dataset = json.loads(
        dataset_path.read_text(encoding="utf-8")
    )

    mock_analysis = {
        "diagnosis": "Insufficient evidence to determine the root cause.",
        "evidence": [],
        "confidence": 0.0,
        "possible_causes": [],
        "recommended_actions": [],
        "verification_steps": [],
    }

    with patch(
        "app.agents.incident_agent.LLMService.analyze",
        return_value=mock_analysis,
    ):
        agent = IncidentAgent()

        assert len(dataset) > 0

        for case in dataset:
            result = agent.analyze(case["incident"])

            assert isinstance(result, dict)
            assert "diagnosis" in result
            assert "confidence" in result
            assert 0.0 <= result["confidence"] <= 1.0
