import asyncio
import logging
import time
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import (
    FastAPI,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import app.services.notification_events

from app.api.v1.routes.activity import (
    router as activity_router,
)
from app.api.v1.routes.ai import (
    router as ai_router,
)
from app.api.v1.routes.audit_findings import (
    router as audit_findings_router,
)
from app.api.v1.routes.audits import (
    router as audits_router,
)
from app.api.v1.routes.auth import (
    router as auth_router,
)
from app.api.v1.routes.control_framework_controls import (
    router as control_framework_controls_router,
)
from app.api.v1.routes.controls import (
    router as controls_router,
)
from app.api.v1.routes.corrective_action_report import (
    router as corrective_action_report_router,
)
from app.api.v1.routes.corrective_actions import (
    router as corrective_actions_router,
)
from app.api.v1.routes.dashboard import (
    router as dashboard_router,
)
from app.api.v1.routes.evidence import (
    router as evidence_router,
)
from app.api.v1.routes.framework_controls import (
    router as framework_controls_router,
)
from app.api.v1.routes.frameworks import (
    router as frameworks_router,
)
from app.api.v1.routes.health import (
    router as health_router,
)
from app.api.v1.routes.intelligence import (
    router as intelligence_router,
)
from app.api.v1.routes.monitoring import (
    router as monitoring_router,
)
from app.api.v1.routes.notifications import (
    router as notifications_router,
)
from app.api.v1.routes.reports import (
    router as reports_router,
)
from app.api.v1.routes.risk_controls import (
    router as risk_controls_router,
)
from app.api.v1.routes.risk_treatments import (
    router as risk_treatments_router,
)
from app.api.v1.routes.risk_trend import (
    router as risk_trend_router,
)
from app.api.v1.routes.risks import (
    router as risks_router,
)
from app.api.v1.routes.users import (
    router as users_router,
)

from app.core.config import (
    CORS_ORIGINS,
    MAX_REQUEST_BODY_BYTES,
)
from app.database.database import engine
from app.exceptions.handlers import (
    register_exception_handlers,
)
from app.services.notification_scheduler import (
    notification_scheduler_loop,
)


logger = logging.getLogger(
    "cybergrc.application"
)

logger.setLevel(logging.INFO)


# ==========================================================
# APPLICATION LIFESPAN
# ==========================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Start background services during application startup
    and cleanly stop them during application shutdown.
    """

    logger.info(
        "application_startup"
    )

    scheduler_task = asyncio.create_task(
        notification_scheduler_loop()
    )

    try:
        yield

    finally:
        logger.info(
            "application_shutdown_started"
        )

        scheduler_task.cancel()

        try:
            await scheduler_task

        except asyncio.CancelledError:
            logger.info(
                "notification_scheduler_cancelled"
            )

        finally:
            engine.dispose()

        logger.info(
            "application_shutdown_completed"
        )


# ==========================================================
# APPLICATION
# ==========================================================


app = FastAPI(
    title="CyberGRC AI",
    description=(
        "AI-Powered Governance, Risk & "
        "Compliance Platform"
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ==========================================================
# REQUEST SIZE LIMIT
# ==========================================================


@app.middleware("http")
async def request_size_limit_middleware(
    request: Request,
    call_next,
):
    """
    Reject requests whose declared Content-Length exceeds
    the configured maximum request body size.

    Requests without Content-Length are allowed through because
    the body may be streamed or transferred using chunked
    encoding.
    """

    content_length = request.headers.get(
        "content-length"
    )

    if content_length is not None:
        try:
            request_size = int(content_length)

        except ValueError:
            return JSONResponse(
                status_code=400,
                content={
                    "detail": "Invalid Content-Length header"
                },
            )

        if request_size > MAX_REQUEST_BODY_BYTES:
            return JSONResponse(
                status_code=413,
                content={
                    "detail": "Request body too large"
                },
            )

    return await call_next(request)


# ==========================================================
# REQUEST CONTEXT + LOGGING
# ==========================================================


@app.middleware("http")
async def request_context_middleware(
    request: Request,
    call_next,
):
    """
    Generate a server-side request ID and log the final
    outcome of each request.

    Only safe request metadata is logged:

    - request ID
    - HTTP method
    - URL path
    - HTTP status
    - request duration

    Query-string values are intentionally excluded because
    URLs may contain sensitive information.
    """

    request_id = str(uuid4())

    request.state.request_id = request_id

    start_time = time.perf_counter()

    try:
        response = await call_next(request)

    except Exception as exc:
        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.error(
            "request_failed "
            "request_id=%s "
            "method=%s "
            "path=%s "
            "exception_type=%s "
            "duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            type(exc).__name__,
            duration_ms,
        )

        raise

    duration_ms = (
        time.perf_counter() - start_time
    ) * 1000

    response.headers[
        "X-Request-ID"
    ] = request_id

    logger.info(
        "request_completed "
        "request_id=%s "
        "method=%s "
        "path=%s "
        "status_code=%s "
        "duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    return response


# ==========================================================
# SECURITY HEADERS
# ==========================================================


@app.middleware("http")
async def security_headers_middleware(
    request: Request,
    call_next,
):
    """
    Apply baseline browser security headers to all
    application responses.

    The normal application uses a strict CSP.

    FastAPI's Swagger UI and ReDoc pages require narrowly
    scoped documentation assets from jsDelivr, so those
    documentation routes receive a dedicated CSP exception.

    The exception is limited to /docs and /redoc and does not
    weaken the CSP used by the application's API or frontend.
    """

    response = await call_next(request)

    response.headers[
        "X-Content-Type-Options"
    ] = "nosniff"

    response.headers[
        "X-Frame-Options"
    ] = "DENY"

    response.headers[
        "Referrer-Policy"
    ] = "no-referrer"

    response.headers[
        "Permissions-Policy"
    ] = (
        "camera=(), microphone=(), "
        "geolocation=()"
    )

    # ------------------------------------------------------
    # Swagger UI
    # ------------------------------------------------------

    if request.url.path == "/docs":

        response.headers[
            "Content-Security-Policy"
        ] = (
            "default-src 'self'; "
            "img-src 'self' data: blob: "
            "https://fastapi.tiangolo.com; "
            "style-src 'self' 'unsafe-inline' "
            "https://cdn.jsdelivr.net; "
            "script-src 'self' 'unsafe-inline' "
            "https://cdn.jsdelivr.net; "
            "font-src 'self' data: "
            "https://cdn.jsdelivr.net; "
            "connect-src 'self' "
            "http://localhost:8000 "
            "http://127.0.0.1:8000; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )

    # ------------------------------------------------------
    # ReDoc
    # ------------------------------------------------------

    elif request.url.path == "/redoc":

        response.headers[
            "Content-Security-Policy"
        ] = (
            "default-src 'self'; "
            "img-src 'self' data: blob: "
            "https://fastapi.tiangolo.com; "
            "style-src 'self' 'unsafe-inline' "
            "https://cdn.jsdelivr.net; "
            "script-src 'self' 'unsafe-inline' "
            "https://cdn.jsdelivr.net; "
            "font-src 'self' data: "
            "https://cdn.jsdelivr.net; "
            "connect-src 'self' "
            "http://localhost:8000 "
            "http://127.0.0.1:8000; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )

    # ------------------------------------------------------
    # Normal application/API
    # ------------------------------------------------------

    else:

        response.headers[
            "Content-Security-Policy"
        ] = (
            "default-src 'self'; "
            "img-src 'self' data: blob:; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; "
            "font-src 'self' data:; "
            "connect-src 'self' "
            "http://localhost:8000 "
            "http://127.0.0.1:8000; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )

    return response


# ==========================================================
# CORS
# ==========================================================


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
    ],
    expose_headers=[
        "X-Request-ID",
    ],
)


# ==========================================================
# EXCEPTION HANDLERS
# ==========================================================


register_exception_handlers(app)


# ==========================================================
# API ROUTES
# ==========================================================


app.include_router(
    health_router,
    prefix="/api/v1",
)

app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    users_router,
    prefix="/api/v1",
)

app.include_router(
    risks_router,
    prefix="/api/v1",
)

app.include_router(
    controls_router,
    prefix="/api/v1",
)

app.include_router(
    risk_controls_router,
    prefix="/api/v1",
)

app.include_router(
    risk_treatments_router,
    prefix="/api/v1",
)

app.include_router(
    frameworks_router,
    prefix="/api/v1",
)

app.include_router(
    framework_controls_router,
    prefix="/api/v1",
)

app.include_router(
    control_framework_controls_router,
    prefix="/api/v1",
)

app.include_router(
    evidence_router,
    prefix="/api/v1",
)

app.include_router(
    audits_router,
    prefix="/api/v1",
)

app.include_router(
    audit_findings_router,
    prefix="/api/v1",
)

app.include_router(
    corrective_actions_router,
    prefix="/api/v1",
)

app.include_router(
    ai_router,
    prefix="/api/v1",
)

app.include_router(
    dashboard_router,
    prefix="/api/v1",
)

app.include_router(
    activity_router,
    prefix="/api/v1",
)

app.include_router(
    notifications_router,
    prefix="/api/v1",
)

app.include_router(
    risk_trend_router,
    prefix="/api/v1",
)

app.include_router(
    reports_router,
    prefix="/api/v1",
)

app.include_router(
    corrective_action_report_router,
    prefix="/api/v1",
)

app.include_router(
    intelligence_router,
    prefix="/api/v1",
)

app.include_router(
    monitoring_router,
    prefix="/api/v1",
)


# ==========================================================
# ROOT
# ==========================================================


@app.get("/")
def root():
    return {
        "message": "Welcome to CyberGRC AI 🚀",
    }