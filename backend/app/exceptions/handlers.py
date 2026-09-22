import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.exceptions import (
    ResourceNotFound,
    DuplicateResource,
    InvalidOperation,
)


logger = logging.getLogger(
    "cybergrc.api.errors"
)


def _request_id(request: Request) -> str:
    """
    Retrieve the server-generated request ID.

    The request ID is created by the request middleware in
    app.main. A fallback is provided for defensive purposes.
    """

    return getattr(
        request.state,
        "request_id",
        "unknown",
    )


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(ResourceNotFound)
    async def resource_not_found_handler(
        request: Request,
        exc: ResourceNotFound,
    ):
        request_id = _request_id(request)

        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": {
                    "type": "ResourceNotFound",
                    "message": (
                        f"{exc.resource} not found."
                    ),
                },
                "request_id": request_id,
            },
            headers={
                "X-Request-ID": request_id,
            },
        )

    @app.exception_handler(DuplicateResource)
    async def duplicate_resource_handler(
        request: Request,
        exc: DuplicateResource,
    ):
        request_id = _request_id(request)

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {
                    "type": "DuplicateResource",
                    "message": (
                        f"{exc.resource} already exists."
                    ),
                },
                "request_id": request_id,
            },
            headers={
                "X-Request-ID": request_id,
            },
        )

    @app.exception_handler(InvalidOperation)
    async def invalid_operation_handler(
        request: Request,
        exc: InvalidOperation,
    ):
        request_id = _request_id(request)

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {
                    "type": "InvalidOperation",
                    "message": exc.message,
                },
                "request_id": request_id,
            },
            headers={
                "X-Request-ID": request_id,
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        request: Request,
        exc: Exception,
    ):
        """
        Handle unexpected application errors without exposing
        exception messages, stack traces, database details,
        credentials, or other internal implementation details.
        """

        request_id = _request_id(request)

        logger.error(
            "unhandled_exception "
            "request_id=%s "
            "method=%s "
            "path=%s "
            "exception_type=%s",
            request_id,
            request.method,
            request.url.path,
            type(exc).__name__,
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "type": "InternalServerError",
                    "message": (
                        "An unexpected error occurred."
                    ),
                    "request_id": request_id,
                },
            },
            headers={
                "X-Request-ID": request_id,
            },
        )