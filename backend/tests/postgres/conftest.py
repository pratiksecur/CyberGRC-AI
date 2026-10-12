"""Fixtures for the real-PostgreSQL test suite.

These tests only run when TEST_DATABASE_URL points at a PostgreSQL database
whose name contains "test". Without it every test here is skipped, so the
normal `python -m pytest -q` keeps working exactly as before.

Do not use pytest-xdist (-n) for this folder: every test shares one database.
"""

import os
from contextlib import asynccontextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401  (make sure every model is registered)
from app.auth.hashing import hash_password
from app.auth.jwt_handler import create_access_token
from app.core.roles import UserRole
from app.database.database import Base, get_db
from app.main import app
from app.models.organization import Organization
from app.models.risk import Risk
from app.models.user import User


@asynccontextmanager
async def _disabled_lifespan(_app):
    yield


# ==========================================================
# DATABASE ENGINE (one per test run)
# ==========================================================

@pytest.fixture(scope="session")
def pg_url():
    raw_url = os.getenv("TEST_DATABASE_URL", "").strip()

    if not raw_url:
        pytest.skip("TEST_DATABASE_URL is not set; PostgreSQL tests skipped.")

    parsed = make_url(raw_url)

    if parsed.get_backend_name() != "postgresql":
        pytest.exit("TEST_DATABASE_URL must be a PostgreSQL URL.", returncode=2)

    # Safety net: these tests DROP and TRUNCATE tables. Never allow them to run
    # against a database that is not clearly a disposable test database.
    if "test" not in (parsed.database or "").lower():
        pytest.exit(
            "Refusing to run: the database name in TEST_DATABASE_URL must "
            "contain the word 'test'.",
            returncode=2,
        )

    return raw_url


@pytest.fixture(scope="session")
def pg_engine(pg_url):
    engine = create_engine(pg_url, pool_pre_ping=True)

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - environment problem
        engine.dispose()
        pytest.exit(
            "Cannot reach the PostgreSQL test database. Start it with "
            f"'docker compose -f docker-compose.test.yml up -d'. ({exc})",
            returncode=2,
        )

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield engine

    engine.dispose()


def _truncate_all(engine) -> None:
    table_names = ", ".join(
        f'"{table.name}"' for table in Base.metadata.sorted_tables
    )

    with engine.begin() as connection:
        connection.execute(
            text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE")
        )


@pytest.fixture()
def pg_session(pg_engine):
    session_factory = sessionmaker(
        bind=pg_engine,
        autoflush=False,
        autocommit=False,
    )

    session = session_factory()

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        _truncate_all(pg_engine)


# ==========================================================
# API CLIENT (same dependency override pattern as tests/conftest.py)
# ==========================================================

@pytest.fixture()
def pg_client(pg_session):
    def override_get_db():
        yield pg_session

    original_lifespan = app.router.lifespan_context

    app.dependency_overrides[get_db] = override_get_db
    app.router.lifespan_context = _disabled_lifespan

    try:
        # Unhandled errors become 500 responses instead of raising, so the
        # endpoint sweep can report every failing route.
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.router.lifespan_context = original_lifespan


# ==========================================================
# TWO ORGANIZATIONS WITH ONE ADMIN AND ONE RISK EACH
# ==========================================================

def _headers_for(user):
    token = create_access_token(data={"sub": user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def pg_tenants(pg_session):
    organization_a = Organization(
        name="PG Organization A", slug="pg-organization-a", is_active=True
    )
    organization_b = Organization(
        name="PG Organization B", slug="pg-organization-b", is_active=True
    )

    pg_session.add_all([organization_a, organization_b])
    pg_session.flush()

    admin_a = User(
        full_name="PG Admin A",
        email="pg-admin-a@example.com",
        hashed_password=hash_password("Password123!"),
        role=UserRole.ADMIN.value,
        manager_id=None,
        department="Executive",
        organization_id=organization_a.id,
    )
    admin_b = User(
        full_name="PG Admin B",
        email="pg-admin-b@example.com",
        hashed_password=hash_password("Password123!"),
        role=UserRole.ADMIN.value,
        manager_id=None,
        department="Executive",
        organization_id=organization_b.id,
    )

    pg_session.add_all([admin_a, admin_b])
    pg_session.flush()

    risk_a = Risk(
        title="Organization A risk",
        description="Visible only to organization A.",
        likelihood=3,
        impact=4,
        risk_score=12,
        organization_id=organization_a.id,
        owner_id=admin_a.id,
        created_by_id=admin_a.id,
    )
    risk_b = Risk(
        title="Organization B risk",
        description="Visible only to organization B.",
        likelihood=2,
        impact=2,
        risk_score=4,
        organization_id=organization_b.id,
        owner_id=admin_b.id,
        created_by_id=admin_b.id,
    )

    pg_session.add_all([risk_a, risk_b])
    pg_session.commit()

    return {
        "org_a": organization_a,
        "org_b": organization_b,
        "admin_a": admin_a,
        "admin_b": admin_b,
        "risk_a": risk_a,
        "risk_b": risk_b,
        "headers_a": _headers_for(admin_a),
        "headers_b": _headers_for(admin_b),
    }