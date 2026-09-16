import pytest
from contextlib import asynccontextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi.testclient import TestClient

from app.database.database import Base, get_db
from app.models.user import User
from app.models.risk import Risk
from app.models.control import Control
from app.models.evidence import Evidence
from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction

from app.core.roles import UserRole
from app.auth.hashing import hash_password
from app.auth.jwt_handler import create_access_token
from app.main import app


# ==========================================================
# TEST LIFESPAN
# ==========================================================

@asynccontextmanager
async def _disabled_lifespan(_app):
    """
    Disable the production application lifespan during API tests.

    The production lifespan starts the notification scheduler,
    which uses the real PostgreSQL SessionLocal.

    API tests use an isolated SQLite database instead, so the
    production scheduler must not run during these tests.

    This affects tests only and does not modify production code.
    """
    yield


# ==========================================================
# DATABASE FIXTURE
# ==========================================================

@pytest.fixture()
def db():
    """
    Create an isolated in-memory SQLite database for each test.

    StaticPool ensures that every connection used during a test
    points to the same in-memory SQLite database.

    The production database remains completely untouched.
    """

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(
        bind=engine
    )

    session = TestingSessionLocal()

    try:
        yield session

    finally:
        session.close()

        Base.metadata.drop_all(
            bind=engine
        )

        engine.dispose()


# ==========================================================
# API CLIENT FIXTURE
# ==========================================================

@pytest.fixture()
def client(db):
    """
    Create a FastAPI TestClient using the isolated SQLite
    database provided by the db fixture.

    The production notification scheduler is disabled for API
    tests so it cannot attempt to connect to the production
    PostgreSQL database.
    """

    def override_get_db():
        try:
            yield db
        finally:
            pass

    original_lifespan = app.router.lifespan_context

    app.dependency_overrides[get_db] = override_get_db
    app.router.lifespan_context = _disabled_lifespan

    try:
        with TestClient(app) as test_client:
            yield test_client

    finally:
        app.dependency_overrides.clear()
        app.router.lifespan_context = original_lifespan


# ==========================================================
# AUTHENTICATION HELPERS
# ==========================================================

@pytest.fixture()
def auth_headers():
    """
    Build Authorization headers for a test user using the
    same JWT creation mechanism used by the application.
    """

    def _headers(user):
        token = create_access_token(
            data={
                "sub": user.email,
            }
        )

        return {
            "Authorization": f"Bearer {token}",
        }

    return _headers


# ==========================================================
# USERS FIXTURE
# ==========================================================

@pytest.fixture()
def users(db):
    """
    Build the standard CyberGRC-AI organizational hierarchy.

    Admin
    └── GRC Manager
        ├── Risk Analyst
        ├── Auditor
        └── Employee
    """

    admin = User(
        id=1,
        full_name="Test Admin",
        email="admin@example.com",
        hashed_password=hash_password("Password123!"),
        role=UserRole.ADMIN.value,
        manager_id=None,
        department="Executive",
    )

    manager = User(
        id=2,
        full_name="Test GRC Manager",
        email="manager@example.com",
        hashed_password=hash_password("Password123!"),
        role=UserRole.GRC_MANAGER.value,
        manager_id=1,
        department="GRC",
    )

    analyst = User(
        id=3,
        full_name="Test Risk Analyst",
        email="analyst@example.com",
        hashed_password=hash_password("Password123!"),
        role=UserRole.RISK_ANALYST.value,
        manager_id=2,
        department="Risk Management",
    )

    auditor = User(
        id=4,
        full_name="Test Auditor",
        email="auditor@example.com",
        hashed_password=hash_password("Password123!"),
        role=UserRole.AUDITOR.value,
        manager_id=2,
        department="Internal Audit",
    )

    employee = User(
        id=5,
        full_name="Test Employee",
        email="employee@example.com",
        hashed_password=hash_password("Password123!"),
        role=UserRole.EMPLOYEE.value,
        manager_id=2,
        department="Operations",
    )

    db.add_all(
        [
            admin,
            manager,
            analyst,
            auditor,
            employee,
        ]
    )

    db.commit()

    for user in [
        admin,
        manager,
        analyst,
        auditor,
        employee,
    ]:
        db.refresh(user)

    return {
        "admin": admin,
        "manager": manager,
        "analyst": analyst,
        "auditor": auditor,
        "employee": employee,
    }


# ==========================================================
# RESOURCE DATA FIXTURE
# ==========================================================

@pytest.fixture()
def resource_data(db, users):
    """
    Create representative GRC records belonging to different
    users so visibility can be tested.
    """

    admin = users["admin"]
    manager = users["manager"]
    analyst = users["analyst"]
    auditor = users["auditor"]
    employee = users["employee"]

    # ======================================================
    # RISKS
    # ======================================================

    risk_admin = Risk(
        title="Admin Risk",
        description="Risk owned by the administrator.",
        likelihood=2,
        impact=3,
        risk_score=6,
        status="Open",
        owner_id=admin.id,
        created_by_id=admin.id,
    )

    risk_manager = Risk(
        title="Manager Risk",
        description="Risk owned by the GRC manager.",
        likelihood=3,
        impact=4,
        risk_score=12,
        status="Open",
        owner_id=manager.id,
        created_by_id=manager.id,
    )

    risk_analyst = Risk(
        title="Analyst Risk",
        description="Risk owned by the risk analyst.",
        likelihood=4,
        impact=4,
        risk_score=16,
        status="Open",
        owner_id=analyst.id,
        created_by_id=analyst.id,
    )

    risk_auditor = Risk(
        title="Auditor Risk",
        description="Risk owned by the auditor.",
        likelihood=4,
        impact=5,
        risk_score=20,
        status="Open",
        owner_id=auditor.id,
        created_by_id=auditor.id,
    )

    risk_employee = Risk(
        title="Employee Risk",
        description="Risk owned by the employee.",
        likelihood=2,
        impact=5,
        risk_score=10,
        status="Open",
        owner_id=employee.id,
        created_by_id=employee.id,
    )

    # ======================================================
    # CONTROLS
    # ======================================================

    control_admin = Control(
        title="Admin Control",
        description="Control owned by the administrator.",
        control_type="Preventive",
        status="Active",
        effectiveness=90,
        owner_id=admin.id,
        created_by_id=admin.id,
    )

    control_analyst = Control(
        title="Analyst Control",
        description="Control owned by the analyst.",
        control_type="Detective",
        status="Active",
        effectiveness=80,
        owner_id=analyst.id,
        created_by_id=analyst.id,
    )

    control_employee = Control(
        title="Employee Control",
        description="Control owned by the employee.",
        control_type="Preventive",
        status="Active",
        effectiveness=70,
        owner_id=employee.id,
        created_by_id=employee.id,
    )

    db.add_all(
        [
            risk_admin,
            risk_manager,
            risk_analyst,
            risk_auditor,
            risk_employee,
            control_admin,
            control_analyst,
            control_employee,
        ]
    )

    db.commit()

    for resource in [
        risk_admin,
        risk_manager,
        risk_analyst,
        risk_auditor,
        risk_employee,
        control_admin,
        control_analyst,
        control_employee,
    ]:
        db.refresh(resource)

    return {
        "risks": {
            "admin": risk_admin,
            "manager": risk_manager,
            "analyst": risk_analyst,
            "auditor": risk_auditor,
            "employee": risk_employee,
        },
        "controls": {
            "admin": control_admin,
            "analyst": control_analyst,
            "employee": control_employee,
        },
    }