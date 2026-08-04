from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.exceptions import (
    ResourceNotFound,
    DuplicateResource,
    InvalidOperation,
)


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(ResourceNotFound)
    async def resource_not_found_handler(
        request: Request,
        exc: ResourceNotFound
    ):
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": {
                    "type": "ResourceNotFound",
                    "message": f"{exc.resource} not found."
                }
            }
        )

    @app.exception_handler(DuplicateResource)
    async def duplicate_resource_handler(
        request: Request,
        exc: DuplicateResource
    ):
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {
                    "type": "DuplicateResource",
                    "message": f"{exc.resource} already exists."
                }
            }
        )

    @app.exception_handler(InvalidOperation)
    async def invalid_operation_handler(
        request: Request,
        exc: InvalidOperation
    ):
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {
                    "type": "InvalidOperation",
                    "message": exc.message
                }
            }
        )