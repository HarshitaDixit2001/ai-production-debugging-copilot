import sys
import json
import math
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.agents.incident_agent import IncidentAgent
from app.evaluation.metrics import (
    calculate_accuracy,
    calculate_diagnosis_coverage,
    diagnosis_matches,
)


DATASET_PATH = ROOT_DIR / "evaluation" / "dataset.json"
REPORT_PATH = ROOT_DIR / "evaluation" / "latest_report.json"

INSUFFICIENT_EVIDENCE_TEXT = (
    "Insufficient evidence to determine the root cause."
)


def is_insufficient_evidence(diagnosis: str) -> bool:
    """Identify diagnoses that explicitly report insufficient evidence."""
    return (
        isinstance(diagnosis, str)
        and "insufficient evidence" in diagnosis.lower()
    )


def normalize_confidence(value):
    """Return a valid confidence score, or None if unavailable or invalid."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None

    confidence = float(value)

    if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
        return None

    return confidence


def main():
    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    agent = IncidentAgent()
    results = []

    for case in dataset:
        incident = case["incident"]
        expected_diagnosis = case["expected_diagnosis"]
        expected_insufficient = is_insufficient_evidence(
            expected_diagnosis
        )

        print(f"Evaluating: {incident}", flush=True)

        try:
            print("Running model analysis...", flush=True)
            analysis = agent.analyze(incident)

            actual_diagnosis = analysis.get("diagnosis", "")
            actual_insufficient = is_insufficient_evidence(
                actual_diagnosis
            )

            passed = diagnosis_matches(
                expected_diagnosis,
                actual_diagnosis,
            )

            result = {
                "incident": incident,
                "expected_diagnosis": expected_diagnosis,
                "actual_diagnosis": actual_diagnosis,
                "passed": passed,
                "confidence": normalize_confidence(
                    analysis.get("confidence")
                ),
                "expected_insufficient_evidence": expected_insufficient,
                "actual_insufficient_evidence": actual_insufficient,
                "insufficient_evidence_handled_correctly": (
                    actual_insufficient == expected_insufficient
                    if expected_insufficient
                    else None
                ),
            }

            results.append(result)

        except Exception as exc:
            results.append({
                "incident": incident,
                "expected_diagnosis": expected_diagnosis,
                "actual_diagnosis": "",
                "passed": False,
                "confidence": None,
                "expected_insufficient_evidence": expected_insufficient,
                "actual_insufficient_evidence": False,
                "insufficient_evidence_handled_correctly": (
                    False if expected_insufficient else None
                ),
                "error": f"{type(exc).__name__}: {exc}",
            })

    accuracy_metrics = calculate_accuracy(results)
    coverage_metrics = calculate_diagnosis_coverage(results)

    insufficient_cases = [
        result for result in results
        if result["expected_insufficient_evidence"]
    ]

    correctly_handled = sum(
        result["insufficient_evidence_handled_correctly"] is True
        for result in insufficient_cases
    )

    valid_confidences = [
        result["confidence"]
        for result in results
        if result["confidence"] is not None
    ]

    report = {
        **accuracy_metrics,
        **coverage_metrics,
        "insufficient_evidence_cases": len(insufficient_cases),
        "insufficient_evidence_correct": correctly_handled,
        "insufficient_evidence_accuracy": (
            round(correctly_handled / len(insufficient_cases), 4)
            if insufficient_cases
            else None
        ),
        "cases_with_valid_confidence": len(valid_confidences),
        "average_confidence": (
            round(sum(valid_confidences) / len(valid_confidences), 4)
            if valid_confidences
            else None
        ),
        "failed_cases": sum(
            result["passed"] is False for result in results
        ),
        "error_cases": sum(
            "error" in result for result in results
        ),
        "results": results,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\nEvaluation Summary")
    print(json.dumps(
        {key: value for key, value in report.items() if key != "results"},
        indent=2,
    ))

    print("\nIndividual Results")
    print(json.dumps(results, indent=2))

    print(f"\nReport saved to: {REPORT_PATH}")


if __name__ == "__main__":
    main()