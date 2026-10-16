import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

DATASET_PATH = Path("evaluation/dataset.json")


def test_evaluation_dataset_has_required_cases():
    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))

    assert len(dataset) >= 4

    for case in dataset:
        assert case["incident"]
        assert case["expected_diagnosis"]
        assert case["expected_root_cause"]
        assert isinstance(case["expected_actions"], list)


def test_evaluation_dataset_includes_insufficient_evidence_case():
    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))

    assert any(
        "insufficient evidence" in case["expected_diagnosis"].lower()
        for case in dataset
    )


def test_evaluation_dataset_has_unique_incidents():
    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    incidents = [case["incident"] for case in dataset]

    assert len(incidents) == len(set(incidents))


def test_evaluation_summary_returns_latest_metrics():
    response = client.get("/evaluation/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_cases"] == 4
    assert data["correct"] == 4
    assert data["accuracy"] == 1.0
    assert data["diagnoses_provided"] == 3
    assert data["coverage"] == 0.75
    assert data["insufficient_evidence_cases"] == 1
    assert data["insufficient_evidence_correct"] == 1
    assert data["insufficient_evidence_accuracy"] == 1.0
    assert data["failed_cases"] == 0
    assert data["error_cases"] == 0


def test_evaluation_summary_does_not_expose_unrelated_report_fields():
    response = client.get("/evaluation/summary")

    assert response.status_code == 200
    assert "results" not in response.json()


def test_evaluation_summary_handles_missing_report(monkeypatch, tmp_path):
    import app.main as main_module

    monkeypatch.setattr(
        main_module,
        "get_evaluation_report_path",
        lambda: tmp_path / "missing_report.json",
    )

    response = client.get("/evaluation/summary")

    assert response.status_code == 503
    assert response.json()["detail"] == "Evaluation report is unavailable."