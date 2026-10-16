from app.tools.evidence_collector import EvidenceCollector


def test_evidence_collector_respects_top_k_per_tool():
    collector = EvidenceCollector()

    results = collector.collect(
        "payment transaction_id HTTP 500",
        top_k=2,
    )

    assert results

    tool_counts = {}

    for result in results:
        tool = result["tool"]
        tool_counts[tool] = tool_counts.get(tool, 0) + 1

    assert all(
        count <= 2
        for count in tool_counts.values()
    )