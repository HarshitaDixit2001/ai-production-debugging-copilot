from app.tools.evidence_collector import EvidenceCollector


def test_payment_500_retrieves_relevant_evidence():
    collector = EvidenceCollector()

    results = collector.collect(
        "POST /payment is returning HTTP 500",
        top_k=5,
    )

    assert results, "Expected evidence for the payment HTTP 500 incident."

    searchable_content = " ".join(
        str(item.get("content", ""))
        for item in results
    ).lower()

    assert (
        "payment" in searchable_content
        or "transaction_id" in searchable_content
        or "500" in searchable_content
    ), "Retrieved evidence did not contain expected incident terms."