import os
from pathlib import Path

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db


router = APIRouter()


APPLICATION_NAME = "CyberGRC AI"
APPLICATION_VERSION = "1.0.0"

UPLOAD_DIR = Path("uploads")


def _not_ready_response():
    """
    Return a generic service-unavailable response.

    Internal database errors, filesystem paths, ownership
    details, and other infrastructure information must not
    be exposed to clients.
    """

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "not_ready",
            "application": APPLICATION_NAME,
        },
    )


@router.get(
    "/health",
    tags=["Health"],
)
def health_check():
    """
    Liveness endpoint.

    Confirms that the FastAPI application process is running.

    This endpoint intentionally does not depend on PostgreSQL
    or persistent upload storage.
    """

    return {
        "status": "healthy",
        "application": APPLICATION_NAME,
        "version": APPLICATION_VERSION,
    }


@router.get(
    "/ready",
    tags=["Health"],
)
def readiness_check(
    db: Session = Depends(get_db),
):
    """
    Readiness endpoint.

    The application is considered ready only when:

    1. PostgreSQL is reachable.
    2. Persistent upload storage exists.
    3. Persistent upload storage is writable.

    This prevents Docker from considering the backend healthy
    when evidence uploads would fail because of a broken or
    incorrectly mounted uploads volume.
    """

    # ------------------------------------------------------
    # Database readiness
    # ------------------------------------------------------

    try:
        db.execute(text("SELECT 1"))

    except SQLAlchemyError:
        return _not_ready_response()

    # ------------------------------------------------------
    # Upload storage readiness
    # ------------------------------------------------------

    try:
        storage_ready = (
            UPLOAD_DIR.is_dir()
            and os.access(
                UPLOAD_DIR,
                os.W_OK,
            )
        )

    except OSError:
        storage_ready = False

    if not storage_ready:
        return _not_ready_response()

    # ------------------------------------------------------
    # Everything required by the application is ready
    # ------------------------------------------------------

    return {
        "status": "ready",
        "application": APPLICATION_NAME,
        "version": APPLICATION_VERSION,
    }