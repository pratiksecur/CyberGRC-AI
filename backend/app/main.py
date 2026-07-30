from fastapi import FastAPI

from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.auth import router as auth_router

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


@app.get("/")
def root():
    return {
        "message": "Welcome to CyberGRC AI 🚀"
    }