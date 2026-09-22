from pathlib import Path
from unittest.mock import Mock

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.routes import health
from app.database.database import get_db
from app.main import app


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _override_db(fake_db):
    def override_get_db():
        yield fake_db

    return override_get_db


def _set_storage_state(
    monkeypatch,
    *,
    is_dir: bool,
    writable: bool,
):
    fake_upload_dir = Mock()
    fake_upload_dir.is_dir.return_value = is_dir

    monkeypatch.setattr(
        health,
        "UPLOAD_DIR",
        fake_upload_dir,
    )

    monkeypatch.setattr(
        health.os,
        "access",
        lambda path, mode: writable,
    )


def test_readiness_requires_writable_upload_storage(
    monkeypatch,
):
    fake_db = Mock()
    fake_db.execute.return_value = None

    _set_storage_state(
        monkeypatch,
        is_dir=True,
        writable=False,
    )

    app.dependency_overrides[get_db] = (
        _override_db(fake_db)
    )

    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/ready"
            )
    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

    assert response.status_code == 503

    data = response.json()

    assert data["status"] == "not_ready"
    assert data["application"] == "CyberGRC AI"

    fake_db.execute.assert_called_once()


def test_readiness_succeeds_when_database_and_storage_are_ready(
    monkeypatch,
):
    fake_db = Mock()
    fake_db.execute.return_value = None

    _set_storage_state(
        monkeypatch,
        is_dir=True,
        writable=True,
    )

    app.dependency_overrides[get_db] = (
        _override_db(fake_db)
    )

    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/ready"
            )
    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ready"
    assert data["application"] == "CyberGRC AI"
    assert data["version"] == "1.0.0"

    fake_db.execute.assert_called_once()


def test_readiness_fails_when_database_is_unavailable(
    monkeypatch,
):
    fake_db = Mock()

    fake_db.execute.side_effect = (
        SQLAlchemyError(
            "database unavailable"
        )
    )

    _set_storage_state(
        monkeypatch,
        is_dir=True,
        writable=True,
    )

    app.dependency_overrides[get_db] = (
        _override_db(fake_db)
    )

    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/ready"
            )
    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

    assert response.status_code == 503

    data = response.json()

    assert data["status"] == "not_ready"

    assert (
        "database unavailable"
        not in response.text
    )


def test_docker_backend_healthcheck_uses_readiness():
    compose_file = (
        PROJECT_ROOT
        / "docker-compose.yml"
    )

    content = compose_file.read_text(
        encoding="utf-8"
    )

    backend_start = content.index(
        "backend:"
    )

    frontend_start = content.index(
        "# ========================================================",
        backend_start + 1,
    )

    backend_section = content[
        backend_start:frontend_start
    ]

    assert (
        "/api/v1/ready"
        in backend_section
    )

    assert (
        "/api/v1/health"
        not in backend_section
    )


def test_backend_dockerfile_prepares_upload_directory():
    dockerfile = (
        PROJECT_ROOT
        / "backend"
        / "Dockerfile"
    )

    content = dockerfile.read_text(
        encoding="utf-8"
    )

    assert (
        "mkdir -p /app/uploads"
        in content
    )

    assert (
        "chown -R appuser:appuser /app"
        in content
    )

    assert (
        "USER appuser"
        in content
    )


def test_operations_runbook_documents_volume_recovery():
    runbook = (
        PROJECT_ROOT
        / "docs"
        / "OPERATIONS.md"
    )

    content = runbook.read_text(
        encoding="utf-8"
    )

    assert (
        "Persistent Upload Volume Ownership"
        in content
    )

    assert (
        "docker compose run --rm --no-deps"
        in content
    )

    assert (
        "--cap-add CHOWN"
        in content
    )

    assert (
        "uploads_data"
        in content
    )