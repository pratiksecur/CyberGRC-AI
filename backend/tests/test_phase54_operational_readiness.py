from unittest.mock import Mock
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.database.database import get_db
from app.main import app


def test_health_endpoint_reports_liveness():
    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["application"] == "CyberGRC AI"
    assert data["version"] == "1.0.0"


def test_readiness_endpoint_reports_database_readiness():
    fake_db = Mock()

    def override_get_db():
        yield fake_db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/ready")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ready"
    assert data["application"] == "CyberGRC AI"
    assert data["version"] == "1.0.0"

    fake_db.execute.assert_called_once()


def test_readiness_returns_503_when_database_is_unavailable():
    fake_db = Mock()
    fake_db.execute.side_effect = SQLAlchemyError(
        "database unavailable"
    )

    def override_get_db():
        yield fake_db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/ready")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 503

    data = response.json()

    assert data["status"] == "not_ready"
    assert data["application"] == "CyberGRC AI"

    assert "database unavailable" not in response.text
    assert "DATABASE_URL" not in response.text


def test_responses_include_valid_request_id():
    with TestClient(app) as client:
        first_response = client.get("/api/v1/health")
        second_response = client.get("/api/v1/health")

    first_request_id = first_response.headers.get(
        "X-Request-ID"
    )

    second_request_id = second_response.headers.get(
        "X-Request-ID"
    )

    assert first_request_id
    assert second_request_id

    UUID(first_request_id)
    UUID(second_request_id)

    assert first_request_id != second_request_id