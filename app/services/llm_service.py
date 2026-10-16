
import json
import logging

from ollama import Client

from app.core.config import settings

logger = logging.getLogger(__name__)

INSUFFICIENT_EVIDENCE = (
    "Insufficient evidence to determine the root cause."
)
ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "diagnosis": {"type": "string"},
        "evidence": {
            "type": "array",
            "items": {"type": "string"},
        },
        "confidence": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
        },
        "possible_causes": {
            "type": "array",
            "items": {"type": "string"},
        },
        "recommended_actions": {
            "type": "array",
            "items": {"type": "string"},
        },
        "verification_steps": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "diagnosis",
        "evidence",
        "confidence",
        "possible_causes",
        "recommended_actions",
        "verification_steps",
    ],
    "additionalProperties": False,
}

class LLMService:
    def analyze(self, incident: str, context: str) -> dict:
        prompt = f"""
You are a production debugging assistant.

Analyze the incident using only the provided evidence.

Incident:
{incident}

Evidence:
{context}

Return only valid JSON with exactly these fields:
{{
  "diagnosis": "string",
  "evidence": ["string"],
  "confidence": 0.0,
  "possible_causes": ["string"],
  "recommended_actions": ["string"],
  "verification_steps": ["string"]
}}

Rules:
- Do not invent facts or evidence.
- Base the diagnosis on the strongest relevant evidence.
- Cite evidence using details present in the supplied context.
- Confidence must be between 0.0 and 1.0.
- If the evidence cannot establish a root cause, use this exact diagnosis:
  "{INSUFFICIENT_EVIDENCE}"
- Recommended actions must be relevant to the evidence.
- Verification steps must explain how to confirm the diagnosis.
"""

        client = Client(timeout=180)

        try:
            response = client.chat(
                model=settings.ollama_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                format=ANALYSIS_SCHEMA,
                options={
                    "temperature": 0,
                    "num_predict": 400,
                    "num_ctx": 4096,
                },
                think=False,
            )

            raw_content = response.message.content
            analysis = json.loads(raw_content)

        except Exception as exc:
            logger.exception(
                "Local LLM analysis failed for incident: %s",
                incident[:200],
            )
            raise RuntimeError(
                "Local LLM analysis failed. Check the Ollama service, "
                "model availability, and application logs."
            ) from exc

        if not isinstance(analysis, dict):
            raise ValueError("LLM response must be a JSON object.")

        required_fields = {
            "diagnosis",
            "evidence",
            "confidence",
            "possible_causes",
            "recommended_actions",
            "verification_steps",
        }

        missing_fields = required_fields - set(analysis)

        if missing_fields:
            raise ValueError(
        f"LLM response is missing required fields: "
        f"{sorted(missing_fields)}"
        )

# Ignore unexpected extra fields while keeping the response schema stable.
        analysis = {
        field: analysis[field]
        for field in required_fields
        }

        if (
            not isinstance(analysis["diagnosis"], str)
            or not analysis["diagnosis"].strip()
        ):
            raise ValueError("LLM diagnosis must be a non-empty string.")

        if (
            not isinstance(analysis["evidence"], list)
            or not all(isinstance(item, str) for item in analysis["evidence"])
        ):
            raise ValueError("LLM evidence must be a list of strings.")

        confidence = analysis["confidence"]
        if (
            not isinstance(confidence, (int, float))
            or isinstance(confidence, bool)
            or not 0.0 <= confidence <= 1.0
        ):
            raise ValueError("LLM confidence must be between 0 and 1.")

        for field in (
            "possible_causes",
            "recommended_actions",
            "verification_steps",
        ):
            if not isinstance(analysis[field], list) or not all(
                isinstance(item, str) for item in analysis[field]
            ):
                raise ValueError(
                    f"LLM field '{field}' must be a list of strings."
                )

        return analysis
