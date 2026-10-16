import logging
import time

from app.agents.incident_agent import IncidentAgent
from app.models.incident import IncidentRequest, IncidentResponse

logger = logging.getLogger(__name__)

agent = IncidentAgent()


def normalize_evidence(evidence: list) -> list[dict]:
    """Normalize AI evidence into the dictionary format required by the API."""
    normalized = []

    for index, item in enumerate(evidence):
        if isinstance(item, dict):
            content = item.get("content", item.get("text", ""))
            source = item.get("source", "AI analysis")

            normalized.append(
                {
                    "source": str(source),
                    "chunk_id": str(item.get("chunk_id", f"evidence-{index + 1}")),
                    "content": str(content),
                    "score": _normalize_score(item.get("score", 0.0)),
                }
            )
        elif isinstance(item, str) and item.strip():
            normalized.append(
                {
                    "source": "AI analysis",
                    "chunk_id": f"evidence-{index + 1}",
                    "content": item.strip(),
                    "score": 0.0,
                }
            )

    return normalized


def _normalize_score(value) -> float:
    """Return a valid evidence score between 0 and 1."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0

    return float(value) if 0.0 <= value <= 1.0 else 0.0


def analyze_incident(request: IncidentRequest) -> IncidentResponse:
    start_time = time.perf_counter()

    logger.info(
        "Incident analysis started | incident=%s",
        request.incident,
    )

    analysis = agent.analyze(request.incident)

    duration_ms = (time.perf_counter() - start_time) * 1000

    logger.info(
        "Incident analysis completed | duration_ms=%.2f | confidence=%s",
        duration_ms,
        analysis.get("confidence"),
    )

    return IncidentResponse(
        incident=request.incident,
        diagnosis=analysis["diagnosis"],
        evidence=normalize_evidence(analysis.get("evidence", [])),
        confidence=analysis["confidence"],
        possible_causes=analysis["possible_causes"],
        recommended_actions=analysis["recommended_actions"],
        verification_steps=analysis["verification_steps"],
    )