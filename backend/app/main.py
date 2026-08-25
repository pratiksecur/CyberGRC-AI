from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.users import router as users_router
from app.api.v1.routes.risks import router as risks_router
from app.api.v1.routes.controls import router as controls_router
from app.api.v1.routes.risk_controls import router as risk_controls_router
from app.api.v1.routes.frameworks import router as frameworks_router
from app.api.v1.routes.framework_controls import router as framework_controls_router
from app.api.v1.routes.control_framework_controls import router as control_framework_controls_router
from app.api.v1.routes.evidence import router as evidence_router
from app.api.v1.routes.audits import router as audits_router
from app.api.v1.routes.audit_findings import router as audit_findings_router
from app.api.v1.routes.corrective_actions import router as corrective_actions_router
from app.api.v1.routes.ai import router as ai_router
from app.api.v1.routes.dashboard import router as dashboard_router
from app.api.v1.routes.activity import router as activity_router
from app.api.v1.routes.risk_trend import router as risk_trend_router
from app.api.v1.routes.reports import router as reports_router
from app.api.v1.routes.corrective_action_report import (
    router as corrective_action_report_router,
)

from app.api.v1.routes.notifications import (
    router as notifications_router,
)

from app.exceptions.handlers import register_exception_handlers


app = FastAPI(
    title="CyberGRC AI",
    description="AI-Powered Governance, Risk & Compliance Platform",
    version="1.0.0"
)

# Serve uploaded evidence files
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register global exception handlers
register_exception_handlers(app)

app.include_router(
    health_router,
    prefix="/api/v1"
)

app.include_router(
    auth_router,
    prefix="/api/v1"
)

app.include_router(
    users_router,
    prefix="/api/v1"
)

app.include_router(
    risks_router,
    prefix="/api/v1"
)

app.include_router(
    controls_router,
    prefix="/api/v1"
)

app.include_router(
    risk_controls_router,
    prefix="/api/v1"
)

app.include_router(
    frameworks_router,
    prefix="/api/v1"
)

app.include_router(
    framework_controls_router,
    prefix="/api/v1"
)

app.include_router(
    control_framework_controls_router,
    prefix="/api/v1"
)

app.include_router(
    evidence_router,
    prefix="/api/v1"
)

app.include_router(
    audits_router,
    prefix="/api/v1"
)

app.include_router(
    audit_findings_router,
    prefix="/api/v1"
)

app.include_router(
    corrective_actions_router,
    prefix="/api/v1"
)

app.include_router(
    ai_router,
    prefix="/api/v1"
)

app.include_router(
    dashboard_router,
    prefix="/api/v1"
)

app.include_router(
    activity_router,
    prefix="/api/v1"
)

app.include_router(
    notifications_router,
    prefix="/api/v1",
)

app.include_router(
    risk_trend_router,
    prefix="/api/v1"
)

app.include_router(
    reports_router,
    prefix="/api/v1"
)

app.include_router(
    corrective_action_report_router,
    prefix="/api/v1"
)


@app.get("/")
def root():
    return {
        "message": "Welcome to CyberGRC AI 🚀"
    }