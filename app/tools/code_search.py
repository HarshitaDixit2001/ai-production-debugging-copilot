
from pathlib import Path

from app.tools.base import BaseIncidentTool
from app.tools.search_utils import extract_query_terms

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were",
    "to", "for", "of", "in", "on", "and", "because",
    "with", "it", "this", "that", "how", "do", "i",
    "post", "get", "put", "delete", "returns", "returning",
}


class CodeSearchTool(BaseIncidentTool):
    name = "code_search"

    def __init__(self, code_dir: str = "data/code_context"):
        project_root = Path(__file__).resolve().parents[2]
        configured_path = Path(code_dir)

        self.code_dir = (
            configured_path
            if configured_path.is_absolute()
            else project_root / configured_path
        )

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        query_terms = extract_query_terms(query)

        if not query_terms:
            return []

        results = []

        if not self.code_dir.exists():
            return results

        for path in self.code_dir.rglob("*.py"):
            try:
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                continue

            for line_number, line in enumerate(content.splitlines(), start=1):
                line_lower = line.lower()
                matched_terms = [
                    term for term in query_terms if term in line_lower
                ]

                if matched_terms:
                    results.append(
                        {
                            "tool": self.name,
                            "source": str(path),
                            "line": line_number,
                            "content": line,
                            "score": len(matched_terms) / max(len(query_terms), 1),
                        }
                    )

        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:max(top_k, 0)]
