import json
import re
from typing import Any


STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were",
    "to", "for", "of", "in", "on", "and", "because",
    "with", "it", "this", "that", "how", "do", "i",
    "post", "get", "put", "delete", "returns", "returning",
    "return", "http", "api", "request", "requests",
    "no", "matching", "logs", "documentation",
}


def extract_query_terms(query: str) -> set[str]:
    """Extract meaningful terms from an incident description."""
    terms = re.findall(r"[a-z0-9]+(?:_[a-z0-9]+)*", query.lower())

    return {
        term
        for term in terms
        if term not in STOP_WORDS and not term.isdigit()
    }


def extract_endpoint(text: str) -> str | None:
    """Extract an API endpoint such as /payment or /unknown."""
    match = re.search(
        r"(?<![\w.])(/[a-zA-Z][a-zA-Z0-9_-]*(?:/[a-zA-Z0-9_-]+)*)",
        text,
    )
    return match.group(1).lower() if match else None


def extract_http_status_codes(text: str) -> set[str]:
    """Extract explicit HTTP status codes such as HTTP 500."""
    return set(
        re.findall(r"\bHTTP\s+([45]\d{2})\b", text, flags=re.IGNORECASE)
    )


def evidence_text(result: dict[str, Any]) -> str:
    """Return searchable evidence content without using its file path."""
    content = result.get("content", "")

    if isinstance(content, str):
        return content

    return json.dumps(content, ensure_ascii=False, default=str)


def is_relevant_evidence(
    query: str,
    result: dict[str, Any],
    minimum_score: float = 0.75,
) -> bool:
    """Reject weak, unrelated, or explicitly conflicting evidence."""
    score = result.get("score", 0)

    if (
        not isinstance(score, (int, float))
        or isinstance(score, bool)
        or score < minimum_score
    ):
        return False

    content = evidence_text(result)
    query_terms = extract_query_terms(query)
    content_terms = extract_query_terms(content)

    # Semantic similarity alone is not enough: require some lexical support.
    if query_terms and not query_terms.intersection(content_terms):
        return False

    query_endpoint = extract_endpoint(query)
    content_endpoint = extract_endpoint(content)

    if (
        query_endpoint
        and content_endpoint
        and query_endpoint != content_endpoint
    ):
        return False

    query_statuses = extract_http_status_codes(query)
    content_statuses = extract_http_status_codes(content)

    # Reject evidence that explicitly describes only a different HTTP status.
    if (
        query_statuses
        and content_statuses
        and not query_statuses.intersection(content_statuses)
    ):
        return False

    return True
