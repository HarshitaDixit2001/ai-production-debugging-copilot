from unittest.mock import patch

from app.tools.code_search import CodeSearchTool
from app.tools.documentation_search import DocumentationSearchTool
from app.tools.evidence_collector import EvidenceCollector
from app.tools.incident_history import IncidentHistoryTool
from app.tools.log_search import LogSearchTool


def test_log_search():
    results = LogSearchTool().search("POST payment HTTP 500")

    assert results
    assert any(
        "HTTP 500" in result["content"]
        for result in results
    )


def test_documentation_search():
    results = DocumentationSearchTool().search("transaction_id")

    assert results


def test_incident_history_search():
    results = IncidentHistoryTool().search(
        "payment HTTP 500 transaction_id"
    )

    assert results
    assert results[0]["incident_id"] == "INC-001"


def test_code_search():
    results = CodeSearchTool().search("transaction_id payment")

    assert results


def test_evidence_collector_continues_when_a_tool_fails():
    collector = EvidenceCollector()

    valid_evidence = {
        "source": "docs/api_documentation.md",
        "chunk_id": "payment-1",
        "content": "The payment endpoint requires transaction_id.",
        "score": 0.9,
    }

    with (
        patch.object(
            collector.tools[0],
            "search",
            side_effect=RuntimeError("Log search unavailable"),
        ),
        patch.object(
            collector.tools[1],
            "search",
            return_value=[valid_evidence],
        ),
        patch.object(
            collector.tools[2],
            "search",
            return_value=[],
        ),
        patch.object(
            collector.tools[3],
            "search",
            return_value=[],
        ),
    ):
        results = collector.collect(
            "payment transaction_id",
            top_k=2,
        )

    assert results
    assert results[0]["source"] == "docs/api_documentation.md"


def test_evidence_collector_ignores_malformed_results():
    collector = EvidenceCollector()

    valid_evidence = {
        "source": "docs/api_documentation.md",
        "chunk_id": "payment-1",
        "content": "The payment endpoint requires transaction_id.",
        "score": 0.9,
    }

    malformed_results = [
        None,
        "not a dictionary",
        {"source": "docs/bad.md", "content": "Missing score"},
        {
            "source": "docs/bad-score.md",
            "content": "Invalid score",
            "score": 5.0,
        },
        valid_evidence,
    ]

    with (
        patch.object(
            collector.tools[0],
            "search",
            return_value=malformed_results,
        ),
        patch.object(
            collector.tools[1],
            "search",
            return_value=[],
        ),
        patch.object(
            collector.tools[2],
            "search",
            return_value=[],
        ),
        patch.object(
            collector.tools[3],
            "search",
            return_value=[],
        ),
    ):
        results = collector.collect(
            "payment transaction_id",
            top_k=5,
        )

    assert results == [valid_evidence]


def test_evidence_collector_returns_highest_scores_first():
    collector = EvidenceCollector()

    lower_score = {
        "source": "docs/low.md",
        "chunk_id": "low",
        "content": "Payment transaction_id database connection pool exhaustion.",
        "score": 0.4,
    }
    higher_score = {
        "source": "docs/high.md",
        "chunk_id": "high",
        "content": "Payment transaction_id database connection pool exhaustion.",
        "score": 0.9,
    }

    with (
        patch(
            "app.tools.evidence_collector.is_relevant_evidence",
            return_value=True,
        ),
        patch.object(
            collector.tools[0],
            "search",
            return_value=[lower_score, higher_score],
        ),
        patch.object(
            collector.tools[1],
            "search",
            return_value=[],
        ),
        patch.object(
            collector.tools[2],
            "search",
            return_value=[],
        ),
        patch.object(
            collector.tools[3],
            "search",
            return_value=[],
        ),
    ):
        results = collector.collect(
            "payment transaction_id",
            top_k=5,
        )

    assert len(results) == 2
    assert results[0]["score"] == 0.9
    assert results[1]["score"] == 0.4
    assert results[0]["chunk_id"] == "high"