from fastapi import APIRouter

from app.models.incident import IncidentRequest, IncidentResponse
from app.services.incident_service import analyze_incident

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
)


@router.post(
    "/analyze",
    response_model=IncidentResponse,
    summary="Analyze a production incident",
    description=(
        "Analyzes a production incident using semantic retrieval, "
        "debugging tools, historical incidents, code context, "
        "and a local LLM."
    ),
)
def analyze_incident_route(request: IncidentRequest):
    return analyze_incident(request)