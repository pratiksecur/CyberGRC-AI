"""Checks that the SQLite-based suite cannot make.

SQLite does not enforce foreign keys by default and is far more forgiving
about types and GROUP BY than PostgreSQL, which is what runs in Docker.
"""

import pytest
from fastapi.routing import APIRoute
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from app.database.database import Base
from app.main import app
from app.models.risk import Risk
from app.models.user import User

pytestmark = pytest.mark.postgres


# ==========================================================
# SCHEMA
# ==========================================================

def test_schema_is_created_for_every_model(pg_engine):
    created = set(inspect(pg_engine).get_table_names())
    expected = set(Base.metadata.tables)

    assert expected <= created, f"Missing tables: {sorted(expected - created)}"


# ==========================================================
# CONSTRAINTS SQLITE DOES NOT ENFORCE
# ==========================================================

def test_foreign_keys_are_enforced(pg_session, pg_tenants):
    orphan = Risk(
        title="Orphan risk",
        description="Owner does not exist.",
        likelihood=1,
        impact=1,
        risk_score=1,
        organization_id=pg_tenants["org_a"].id,
        owner_id=999999,
        created_by_id=pg_tenants["admin_a"].id,
    )

    pg_session.add(orphan)

    with pytest.raises(IntegrityError):
        pg_session.flush()

    pg_session.rollback()


def test_user_email_must_be_unique(pg_session, pg_tenants):
    duplicate = User(
        full_name="Duplicate",
        email=pg_tenants["admin_a"].email,
        hashed_password="not-a-real-hash",
        role=pg_tenants["admin_a"].role,
        organization_id=pg_tenants["org_a"].id,
    )

    pg_session.add(duplicate)

    with pytest.raises(IntegrityError):
        pg_session.flush()

    pg_session.rollback()


# ==========================================================
# TENANT ISOLATION THROUGH THE REAL API
# ==========================================================

def test_risk_list_only_returns_own_organization(pg_client, pg_tenants):
    response_a = pg_client.get("/api/v1/risks/", headers=pg_tenants["headers_a"])
    response_b = pg_client.get("/api/v1/risks/", headers=pg_tenants["headers_b"])

    assert response_a.status_code == 200, response_a.text
    assert response_b.status_code == 200, response_b.text

    ids_a = {item["id"] for item in response_a.json()}
    ids_b = {item["id"] for item in response_b.json()}

    assert ids_a == {pg_tenants["risk_a"].id}
    assert ids_b == {pg_tenants["risk_b"].id}


def test_cannot_read_another_organizations_risk_by_id(pg_client, pg_tenants):
    response = pg_client.get(
        f"/api/v1/risks/{pg_tenants['risk_b'].id}",
        headers=pg_tenants["headers_a"],
    )

    assert response.status_code in (403, 404), response.text


# ==========================================================
# ENDPOINT SWEEP: NO GET ENDPOINT MAY CRASH ON POSTGRESQL
# ==========================================================

# AI endpoints call a local model server; health/metrics use their own
# connections. They are covered elsewhere.
_EXCLUDED_PREFIXES = (
    "/api/v1/ai",
    "/api/v1/ready",
    "/api/v1/health",
    "/ready",
    "/health",
    "/metrics",
)


def _sweep_paths():
    paths = set()

    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        if "GET" not in route.methods or "{" in route.path:
            continue
        if route.path.startswith(_EXCLUDED_PREFIXES):
            continue
        paths.add(route.path)

    return sorted(paths)


@pytest.mark.parametrize("path", _sweep_paths())
def test_get_endpoint_does_not_crash(pg_client, pg_tenants, path):
    response = pg_client.get(path, headers=pg_tenants["headers_a"])

    assert response.status_code < 500, (
        f"GET {path} returned {response.status_code}: {response.text[:600]}"
    )