from app.evaluation.metrics import (
    calculate_accuracy,
    calculate_diagnosis_coverage,
    diagnosis_matches,
)
from app.evaluation.metrics import diagnosis_matches

def test_diagnosis_coverage_counts_specific_diagnoses():
    results = [
        {
            "actual_diagnosis": "Database insertion failed because transaction_id was NULL.",
            "passed": True,
        },
        {
            "actual_diagnosis": "Insufficient evidence to determine the root cause.",
            "passed": False,
        },
        {
            "actual_diagnosis": "",
            "passed": False,
        },
    ]

    report = calculate_diagnosis_coverage(results)

    assert report["total_cases"] == 3
    assert report["diagnoses_provided"] == 1
    assert report["coverage"] == 0.3333


def test_empty_results_return_zero_metrics():
    assert calculate_accuracy([]) == {
        "total_cases": 0,
        "correct": 0,
        "accuracy": 0.0,
    }

    assert calculate_diagnosis_coverage([]) == {
        "total_cases": 0,
        "diagnoses_provided": 0,
        "coverage": 0.0,
    }


def test_diagnosis_matches_expected_root_cause():
    expected = "Database insertion failed because transaction_id was NULL."
    actual = "Database insertion failed because transaction_id was NULL."

    assert diagnosis_matches(expected, actual) is True

def test_diagnosis_matches_equivalent_wording():
    assert diagnosis_matches(
    "Database connection pool exhaustion is causing payment requests to time out.",
    "Payment API request timing out due to database connection pool exhaustion or long-running queries.",
)

def test_diagnosis_matches_required_currency():
    assert diagnosis_matches(
    "Payment request validation failed because currency is required.",
    "Request validation failed because currency is required.",
)

def test_diagnosis_does_not_match_unrelated_root_cause():
    assert not diagnosis_matches(
    "Database insertion failed because transaction_id was NULL.",
    "Request validation failed because currency is required.",
)

def test_diagnosis_does_not_match_empty_output():
    assert not diagnosis_matches(
    "Database insertion failed because transaction_id was NULL.",
    "",
)