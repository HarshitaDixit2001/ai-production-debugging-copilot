from app.knowledge.indexer import KnowledgeBase
from app.retrieval.context_builder import ContextBuilder
from app.services.llm_service import LLMService
from app.tools.evidence_collector import EvidenceCollector
from app.tools.search_utils import (
    evidence_text,
    extract_endpoint,
    is_relevant_evidence,
)


class IncidentAgent:
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.context_builder = ContextBuilder()
        self.llm_service = LLMService()
        self.evidence_collector = EvidenceCollector()

        self.knowledge_base.build()

    def _insufficient_evidence(self) -> dict:
        return {
            "diagnosis": (
                "Insufficient evidence to determine the root cause."
            ),
            "evidence": [],
            "confidence": 0.0,
            "possible_causes": [],
            "recommended_actions": [
                "Collect relevant application logs and error details.",
                "Verify the affected endpoint and recent changes.",
            ],
            "verification_steps": [
                "Reproduce the incident and collect diagnostic evidence."
            ],
        }

    def analyze(self, incident: str) -> dict:
        rag_results = self.knowledge_base.search(
            incident,
            top_k=5,
        )

        evidence = [
            {
                "source": item["source"],
                "chunk_id": item.get("chunk_id", "rag"),
                "content": item["content"],
                "score": item.get("score", 0.0),
            }
            for item in rag_results
            if isinstance(item, dict)
            and isinstance(item.get("content"), (str, dict))
            and bool(item.get("content"))
        ]

        evidence = [
            item
            for item in evidence
            if is_relevant_evidence(
                incident,
                item,
                minimum_score=0.35,
            )
        ]

        tool_results = self.evidence_collector.collect(
            incident,
            top_k=5,
        )

        for result in tool_results:
            if not isinstance(result, dict):
                continue

            content = result.get("content", "")

            score = result.get("score", 0.0)

            if (
                not isinstance(content, (str, dict))
                or not content
                or isinstance(score, bool)
                or not isinstance(score, (int, float))
                or not 0.0 < score <= 1.0
            ):
                continue

            evidence.append(
                {
                    "source": result.get("source", "tool"),
                    "chunk_id": result.get(
                        "chunk_id",
                        result.get(
                            "line",
                            result.get("incident_id", "tool"),
                        ),
                    ),
                    "content": content,
                    "score": score,
                }
            )

        # Reject invalid evidence records and scores.
        evidence = [
            item
            for item in evidence
            if isinstance(item.get("score"), (int, float))
            and not isinstance(item.get("score"), bool)
            and 0.0 < item["score"] <= 1.0
        ]

        # Require evidence associated with the requested endpoint.
        query_endpoint = extract_endpoint(incident)

        if query_endpoint:
            matching_endpoint_evidence = [
                item
                for item in evidence
                if extract_endpoint(evidence_text(item))
                == query_endpoint
            ]

            if not matching_endpoint_evidence:
                return self._insufficient_evidence()

            evidence = [
                item
                for item in evidence
                if extract_endpoint(evidence_text(item))
                in (None, query_endpoint)
            ]

        if not evidence:
            return self._insufficient_evidence()

        # Build model context from the validated source records.
        context = self.context_builder.build(evidence)

        analysis = self.llm_service.analyze(
            incident=incident,
            context=context,
        )

        required_fields = {
            "diagnosis",
            "evidence",
            "confidence",
            "possible_causes",
            "recommended_actions",
            "verification_steps",
        }

        if not isinstance(analysis, dict):
            return self._insufficient_evidence()

        if not required_fields.issubset(analysis):
            return self._insufficient_evidence()

        valid_analysis = (
            isinstance(analysis.get("diagnosis"), str)
            and bool(analysis["diagnosis"].strip())
            and isinstance(analysis.get("evidence"), list)
            and all(
                isinstance(item, str)
                for item in analysis["evidence"]
            )
            and isinstance(analysis.get("confidence"), (int, float))
            and not isinstance(analysis.get("confidence"), bool)
            and 0.0 <= analysis["confidence"] <= 1.0
            and isinstance(analysis.get("possible_causes"), list)
            and all(
                isinstance(item, str)
                for item in analysis["possible_causes"]
            )
            and isinstance(analysis.get("recommended_actions"), list)
            and all(
                isinstance(item, str)
                for item in analysis["recommended_actions"]
            )
            and isinstance(analysis.get("verification_steps"), list)
            and all(
                isinstance(item, str)
                for item in analysis["verification_steps"]
            )
        )

        if not valid_analysis:
            return self._insufficient_evidence()

        # Use the LLM for analysis, but use retrieved records as evidence.
        analysis["evidence"] = evidence

        return analysis