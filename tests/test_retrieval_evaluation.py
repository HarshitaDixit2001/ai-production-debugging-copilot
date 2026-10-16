from app.knowledge.indexer import KnowledgeBase


def test_retrieval_finds_payment_evidence():
    knowledge_base = KnowledgeBase()
    knowledge_base.build()

    results = knowledge_base.search(
        "POST /payment HTTP 500 transaction_id",
        top_k=5,
    )

    assert results, "Retrieval returned no results for the payment incident."

    sources = [
        result.get("source", "")
        for result in results
        if isinstance(result, dict)
    ]

    assert any(
        "payment" in source.lower()
        for source in sources
    ), f"No payment-related source found. Sources: {sources}"


def test_retrieval_returns_transaction_id_evidence():
    knowledge_base = KnowledgeBase()
    knowledge_base.build()

    results = knowledge_base.search(
        "payment database error NULL transaction_id",
        top_k=5,
    )

    assert results, "Retrieval returned no results for the transaction_id query."

    searchable_content = " ".join(
        str(result.get("content", ""))
        for result in results
        if isinstance(result, dict)
    ).lower()

    assert (
        "transaction_id" in searchable_content
        or "database" in searchable_content
        or "null" in searchable_content
    ), (
        "Results were returned, but none contained relevant database evidence."
    )
