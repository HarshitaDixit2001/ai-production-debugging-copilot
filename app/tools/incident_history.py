
import json
from pathlib import Path

from app.tools.base import BaseIncidentTool
from app.tools.search_utils import extract_query_terms

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were",
    "to", "for", "of", "in", "on", "and", "because",
    "with", "it", "this", "that", "how", "do", "i",
    "post", "get", "put", "delete", "returns", "returning",
}


class IncidentHistoryTool(BaseIncidentTool):
    name = "incident_history"

    def __init__(self, history_file: str = "data/incidents/incident_history.json"):
        project_root = Path(__file__).resolve().parents[2]
        configured_path = Path(history_file)

        self.history_file = (
            configured_path
            if configured_path.is_absolute()
            else project_root / configured_path
        )

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if top_k <= 0 or not self.history_file.exists():
            return []

        try:
            incidents = json.loads(
                self.history_file.read_text(encoding="utf-8")
            )
        except (OSError, UnicodeError, json.JSONDecodeError):
            return []

        query_terms = extract_query_terms(query)

        if not query_terms:
            return []

        if not query_terms:
            return []

        results = []

        for incident in incidents:
            searchable = " ".join(
                [
                    incident.get("title", ""),
                    incident.get("description", ""),
                    incident.get("root_cause", ""),
                    incident.get("service", ""),
                    incident.get("resolution", ""),
                    " ".join(incident.get("evidence", [])),
                ]
            ).lower()

            matched_terms = {
                term for term in query_terms if term in searchable
            }

            if matched_terms:
                results.append(
                    {
                        "tool": self.name,
                        "source": str(self.history_file),
                        "incident_id": incident.get("incident_id", "unknown"),
                        "content": incident,
                        "score": len(matched_terms) / len(query_terms),
                    }
                )

        results.sort(
            key=lambda result: result["score"],
            reverse=True,
        )

        return results[:top_k]
