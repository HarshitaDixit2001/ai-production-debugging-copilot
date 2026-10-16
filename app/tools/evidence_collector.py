from app.tools.code_search import CodeSearchTool
from app.tools.documentation_search import DocumentationSearchTool
from app.tools.incident_history import IncidentHistoryTool
from app.tools.log_search import LogSearchTool
from app.tools.search_utils import is_relevant_evidence


class EvidenceCollector:
    def __init__(self):
        self.tools = [
            LogSearchTool(),
            DocumentationSearchTool(),
            IncidentHistoryTool(),
            CodeSearchTool(),
        ]

    @staticmethod
    def _valid_result(result) -> bool:
        if not isinstance(result, dict):
            return False

        content = result.get("content")
        score = result.get("score")

        if not isinstance(content, (str, dict)) or not content:
            return False

        if isinstance(score, bool) or not isinstance(score, (int, float)):
            return False

        if not 0.0 < score <= 1.0:
            return False

        source = result.get("source")
        return isinstance(source, str) and bool(source.strip())

    def collect(self, query: str, top_k: int = 5) -> list[dict]:
        if not isinstance(query, str) or not query.strip() or top_k <= 0:
            return []

        evidence = []
        candidate_limit = top_k * 5

        for tool in self.tools:
            try:
                results = tool.search(query, top_k=candidate_limit)
            except Exception:
                # A failed source should not prevent other tools from running.
                continue

            if not isinstance(results, list):
                continue

            relevant_results = []

            for result in results:
                if not self._valid_result(result):
                    continue

                try:
                    if is_relevant_evidence(query, result):
                        relevant_results.append(result)
                except (TypeError, ValueError, AttributeError):
                    continue

            relevant_results.sort(
                key=lambda item: item["score"],
                reverse=True,
            )

            evidence.extend(relevant_results[:top_k])

        evidence.sort(key=lambda item: item["score"], reverse=True)

        return evidence[: top_k * len(self.tools)]