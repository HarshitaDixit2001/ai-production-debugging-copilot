from app.knowledge.indexer import KnowledgeBase


def test_retrieval_respects_top_k():
    knowledge_base = KnowledgeBase()
    knowledge_base.build()

    results = knowledge_base.search(
        "payment transaction_id",
        top_k=3,
    )

    assert len(results) <= 3