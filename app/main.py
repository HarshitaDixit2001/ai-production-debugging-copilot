import uuid
import json
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes.incidents import router as incident_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from ollama import Client
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
logger = logging.getLogger(__name__)
setup_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-powered production incident diagnosis system "
        "using retrieval, debugging tools, and local LLM analysis."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)

app.include_router(incident_router)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    incoming_request_id = request.headers.get("X-Request-ID", "").strip()

    if (
        incoming_request_id
        and len(incoming_request_id) <= 128
        and all(
            character.isalnum() or character in "-_.:"
            for character in incoming_request_id
        )
    ):
        request_id = incoming_request_id
    else:
        request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Unhandled application exception | request_id=%s | path=%s",
            request_id,
            request.url.path,
        )
        response = JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "request_id": request_id,
            },
        )

    response.headers["X-Request-ID"] = request_id
    return response

@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
)
def health_check():
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    request_id = getattr(request.state, "request_id", "unknown")

    logger.exception(
        "Unhandled application exception | request_id=%s | path=%s",
        request_id,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
        },
    )


@app.get("/ready")
def readiness_check():
    try:
        client = Client()
        client.show(settings.ollama_model)

        return {
            "status": "ready",
            "model": settings.ollama_model,
        }
    except Exception:
        logger.exception("Ollama readiness check failed")

        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "detail": "Ollama model is unavailable.",
            },
        )

# @app.get(
#     "/evaluation/summary",
#     tags=["Evaluation"],
#     summary="Get the latest evaluation summary",
# )


def get_evaluation_report_path() -> Path:
    return (
        Path(__file__).resolve().parent.parent
        / "evaluation"
        / "latest_report.json"
    )


@app.get(
    "/evaluation/summary",
    tags=["Evaluation"],
    summary="Get the latest evaluation summary",
)
def evaluation_summary():
    report_path = get_evaluation_report_path()

    try:
        with report_path.open("r", encoding="utf-8") as report_file:
            report = json.load(report_file)
    except (OSError, json.JSONDecodeError):
        return JSONResponse(
            status_code=503,
            content={"detail": "Evaluation report is unavailable."},
        )

    if not isinstance(report, dict):
        return JSONResponse(
            status_code=503,
            content={"detail": "Evaluation report has an invalid format."},
        )

    metric_fields = [
        "total_cases",
        "correct",
        "accuracy",
        "diagnoses_provided",
        "coverage",
        "insufficient_evidence_cases",
        "insufficient_evidence_correct",
        "insufficient_evidence_accuracy",
        "average_confidence",
        "failed_cases",
        "error_cases",
    ]

    return {
        key: report[key]
        for key in metric_fields
        if key in report
    }

def readiness_check():
    from fastapi.responses import JSONResponse

    from app.core.config import settings

    try:
        client = Client()
        client.show(settings.ollama_model)

        return {
            "status": "ready",
            "model": settings.ollama_model,
        }
    except Exception:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "reason": "Configured Ollama model is unavailable",
            },
        )