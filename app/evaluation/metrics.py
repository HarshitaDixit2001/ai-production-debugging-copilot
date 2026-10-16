import re


def normalize_text(text: str) -> str:
    """Normalize text for consistent diagnosis comparison."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s_]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def diagnosis_matches(expected: str, actual: str) -> bool:
    """Compare diagnoses using key causal terms and wording overlap."""
    expected_normalized = normalize_text(expected)
    actual_normalized = normalize_text(actual)

    if not expected_normalized or not actual_normalized:
        return False

    if expected_normalized in actual_normalized:
        return True

    expected_words = set(expected_normalized.split())
    actual_words = set(actual_normalized.split())

    # Recognize equivalent descriptions of known causes.
    cause_groups = [
        {"transaction_id", "null"},
        {"connection", "pool", "exhaustion"},
        {"currency", "required"},
    ]

    for cause in cause_groups:
        if cause.issubset(expected_words) and cause.issubset(actual_words):
            return True

    ignored_words = {
        "the", "a", "an", "is", "was", "because", "due", "to",
        "failed", "failure", "causing", "cause",
    }

    expected_meaningful = expected_words - ignored_words
    actual_meaningful = actual_words - ignored_words

    if not expected_meaningful:
        return False

    overlap = len(expected_meaningful & actual_meaningful)
    return overlap / len(expected_meaningful) >= 0.7


def calculate_accuracy(results: list[dict]) -> dict:
    """Return an accuracy report compatible with the evaluation tests."""
    total_cases = len(results)
    correct = sum(bool(result.get("passed", False)) for result in results)

    return {
        "total_cases": total_cases,
        "correct": correct,
        "accuracy": correct / total_cases if total_cases else 0.0,
    }


def calculate_diagnosis_coverage(results: list[dict]) -> dict:
    """Return a report describing how often diagnoses were provided."""
    total_cases = len(results)
    insufficient_text = "insufficient evidence to determine the root cause"

    diagnosed = sum(
        bool(
            str(
                result.get("actual_diagnosis", result.get("actual", ""))
            ).strip()
        )
        and insufficient_text not in normalize_text(
            str(result.get("actual_diagnosis", result.get("actual", "")))
        )
        for result in results
    )

    return {
        "total_cases": total_cases,
        "diagnoses_provided": diagnosed,
        "coverage": round(diagnosed / total_cases, 4) if total_cases else 0.0,
    }