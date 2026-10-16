from app.evaluation.metrics import calculate_accuracy


def test_calculate_accuracy():
    results = [
        {"passed": True},
        {"passed": True},
        {"passed": False},
        {"passed": True},
    ]

    report = calculate_accuracy(results)

    assert report["total_cases"] == 4
    assert report["correct"] == 3
    assert report["accuracy"] == 0.75


def test_calculate_accuracy_with_no_results():
    report = calculate_accuracy([])

    assert report == {
        "total_cases": 0,
        "correct": 0,
        "accuracy": 0.0,
    }
