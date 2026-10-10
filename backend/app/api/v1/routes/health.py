import os
from pathlib import Path

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import PROJECT_NAME, PROJECT_VERSION
from app.database.database import get_db


router = APIRouter()

APPLICATION_NAME = PROJECT_NAME
APPLICATION_VERSION = PROJECT_VERSION
UPLOAD_DIR = Path("uploads")


def _not_ready_response():
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "not_ready", "application": APPLICATION_NAME},
    )


@router.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "application": APPLICATION_NAME,
        "version": APPLICATION_VERSION,
    }


@router.get("/ready", tags=["Health"])
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return _not_ready_response()

    try:
        storage_ready = UPLOAD_DIR.is_dir() and os.access(UPLOAD_DIR, os.W_OK)
    except OSError:
        storage_ready = False

    if not storage_ready:
        return _not_ready_response()

    return {
        "status": "ready",
        "application": APPLICATION_NAME,
        "version": APPLICATION_VERSION,
    }
