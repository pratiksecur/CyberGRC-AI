import asyncio
import logging

from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.database import database
from app.main import app, lifespan


def test_request_logging_contains_request_id_and_safe_metadata(
    caplog,
):
    caplog.set_level(
        logging.INFO,
        logger="cybergrc.application",
    )

    with TestClient(app) as client:
        response = client.get("/")

    request_id = response.headers.get(
        "X-Request-ID"
    )

    assert response.status_code == 200
    assert request_id

    messages = [
        record.getMessage()
        for record in caplog.records
        if record.name
        == "cybergrc.application"
    ]

    matching_messages = [
        message
        for message in messages
        if (
            "request_completed" in message
            and request_id in message
        )
    ]

    assert matching_messages


def test_unexpected_exception_returns_safe_500_response():
    router = APIRouter()

    route_path = (
        "/api/v1/__phase54_unexpected_error"
    )

    @router.get(route_path)
    def raise_unexpected_error():
        raise RuntimeError(
            "super-secret internal database password"
        )

    app.include_router(router)

    try:
        with TestClient(
            app,
            raise_server_exceptions=False,
        ) as client:

            response = client.get(
                route_path
            )

        assert response.status_code == 500

        data = response.json()

        assert data["success"] is False

        assert (
            data["error"]["type"]
            == "InternalServerError"
        )

        assert (
            data["error"]["message"]
            == "An unexpected error occurred."
        )

        assert (
            "super-secret internal database password"
            not in response.text
        )

        request_id = data["error"]["request_id"]

        assert request_id

        assert (
            response.headers.get(
                "X-Request-ID"
            )
            == request_id
        )

    finally:
        app.router.routes[:] = [
            route
            for route in app.router.routes
            if getattr(
                route,
                "path",
                None,
            )
            != route_path
        ]


def test_shutdown_cancels_scheduler_and_disposes_database(
    monkeypatch,
):
    cancelled = False
    disposed = False

    scheduler_started = asyncio.Event()

    async def fake_scheduler():
        nonlocal cancelled

        scheduler_started.set()

        try:
            await asyncio.Event().wait()

        except asyncio.CancelledError:
            cancelled = True
            raise

    def fake_dispose():
        nonlocal disposed
        disposed = True

    monkeypatch.setattr(
        "app.main.notification_scheduler_loop",
        fake_scheduler,
    )

    monkeypatch.setattr(
        "app.main.engine",
        database.engine,
    )

    original_dispose = database.engine.dispose

    database.engine.dispose = fake_dispose

    async def run_lifespan():
        async with lifespan(app):
            await asyncio.wait_for(
                scheduler_started.wait(),
                timeout=1.0,
            )

    try:
        asyncio.run(
            run_lifespan()
        )

    finally:
        database.engine.dispose = (
            original_dispose
        )

    assert cancelled is True
    assert disposed is True


def test_existing_resource_not_found_error_shape_is_preserved():
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/risks/999999999"
        )

    assert response.status_code in {
        401,
        404,
    }

    if response.status_code == 404:
        data = response.json()

        assert data["success"] is False

        assert (
            data["error"]["type"]
            == "ResourceNotFound"
        )

        assert data["error"]["message"]