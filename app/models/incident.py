from pydantic import BaseModel, Field


class IncidentRequest(BaseModel):
    incident: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="A description of the production incident.",
    )


class IncidentResponse(BaseModel):
    incident: str
    diagnosis: str
    evidence: list[dict] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    possible_causes: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    verification_steps: list[str] = Field(default_factory=list)