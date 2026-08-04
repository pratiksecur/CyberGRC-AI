from fastapi import FastAPI

from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.users import router as users_router
from app.api.v1.routes.risks import router as risks_router
from app.api.v1.routes.controls import router as controls_router
from app.api.v1.routes.risk_controls import router as risk_controls_router
from app.api.v1.routes.frameworks import router as frameworks_router
from app.api.v1.routes.framework_controls import router as framework_controls_router
from app.api.v1.routes.control_framework_controls import router as control_framework_controls_router


app = FastAPI(
    title="CyberGRC AI",
    description="AI-Powered Governance, Risk & Compliance Platform",
    version="1.0.0"
)


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

@app.get("/")
def root():
    return {
        "message": "Welcome to CyberGRC AI 🚀"
    }