import pytest
from contextlib import asynccontextmanager
from app.models.framework import Framework
from datetime import date, timedelta

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


@asynccontextmanager
async def _disabled_lifespan(_app):
    yield


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db):
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


@pytest.fixture()
def auth_headers():
    def _headers(user):
        token = create_access_token(
            data={"sub": user.email}
        )

        return {
            "Authorization": f"Bearer {token}"
        }

    return _headers


@pytest.fixture()
def users(db):
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


@pytest.fixture()
def resource_data(db, users):
    admin = users["admin"]
    manager = users["manager"]
    analyst = users["analyst"]
    auditor = users["auditor"]
    employee = users["employee"]

    # ---------------------------------------------------------
    # RISKS
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # CONTROLS
    # ---------------------------------------------------------

    control_admin = Control(
        title="Admin Control",
        description="Control owned by the administrator.",
        control_type="Preventive",
        status="Active",
        effectiveness=90,
        owner_id=admin.id,
        created_by_id=admin.id,
    )

    control_manager = Control(
        title="Manager Control",
        description="Control owned by the GRC manager.",
        control_type="Preventive",
        status="Active",
        effectiveness=85,
        owner_id=manager.id,
        created_by_id=manager.id,
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

    control_auditor = Control(
        title="Auditor Control",
        description="Control owned by the auditor.",
        control_type="Detective",
        status="Active",
        effectiveness=75,
        owner_id=auditor.id,
        created_by_id=auditor.id,
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
            control_manager,
            control_analyst,
            control_auditor,
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
        control_manager,
        control_analyst,
        control_auditor,
        control_employee,
    ]:
        db.refresh(resource)

    # ---------------------------------------------------------
    # EVIDENCE
    # ---------------------------------------------------------

    evidence_admin = Evidence(
        title="Admin Evidence",
        description="Evidence associated with administrator control.",
        control_id=control_admin.id,
        file_name="admin_evidence.pdf",
        file_path="/test/admin_evidence.pdf",
        uploaded_by=admin.id,
    )

    evidence_manager = Evidence(
        title="Manager Evidence",
        description="Evidence associated with manager control.",
        control_id=control_manager.id,
        file_name="manager_evidence.pdf",
        file_path="/test/manager_evidence.pdf",
        uploaded_by=manager.id,
    )

    evidence_analyst = Evidence(
        title="Analyst Evidence",
        description="Evidence associated with analyst control.",
        control_id=control_analyst.id,
        file_name="analyst_evidence.pdf",
        file_path="/test/analyst_evidence.pdf",
        uploaded_by=analyst.id,
    )

    evidence_auditor = Evidence(
        title="Auditor Evidence",
        description="Evidence associated with auditor control.",
        control_id=control_auditor.id,
        file_name="auditor_evidence.pdf",
        file_path="/test/auditor_evidence.pdf",
        uploaded_by=auditor.id,
    )

    evidence_employee = Evidence(
        title="Employee Evidence",
        description="Evidence associated with employee control.",
        control_id=control_employee.id,
        file_name="employee_evidence.pdf",
        file_path="/test/employee_evidence.pdf",
        uploaded_by=employee.id,
    )

    db.add_all(
        [
            evidence_admin,
            evidence_manager,
            evidence_analyst,
            evidence_auditor,
            evidence_employee,
        ]
    )

    db.commit()

    for evidence in [
        evidence_admin,
        evidence_manager,
        evidence_analyst,
        evidence_auditor,
        evidence_employee,
    ]:
        db.refresh(evidence)

    # ---------------------------------------------------------
    # FRAMEWORK
    # ---------------------------------------------------------

    framework = Framework(
        name="Test Compliance Framework",
        version="1.0",
        description="Framework used for authorization matrix tests.",
    )

    db.add(framework)
    db.commit()
    db.refresh(framework)

    # ---------------------------------------------------------
    # AUDITS
    # ---------------------------------------------------------

    audit_admin = Audit(
        name="Admin Audit",
        framework_id=framework.id,
        auditor_id=admin.id,
        created_by_id=admin.id,
        scope="Organization",
        status="Planned",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30),
    )

    audit_manager = Audit(
        name="Manager Audit",
        framework_id=framework.id,
        auditor_id=manager.id,
        created_by_id=manager.id,
        scope="GRC Department",
        status="Planned",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30),
    )

    audit_analyst = Audit(
        name="Analyst Audit",
        framework_id=framework.id,
        auditor_id=analyst.id,
        created_by_id=analyst.id,
        scope="Risk Management",
        status="Planned",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30),
    )

    audit_auditor = Audit(
        name="Auditor Audit",
        framework_id=framework.id,
        auditor_id=auditor.id,
        created_by_id=auditor.id,
        scope="Internal Audit",
        status="Planned",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30),
    )

    audit_employee = Audit(
        name="Employee Audit",
        framework_id=framework.id,
        auditor_id=employee.id,
        created_by_id=employee.id,
        scope="Operations",
        status="Planned",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30),
    )

    db.add_all(
        [
            audit_admin,
            audit_manager,
            audit_analyst,
            audit_auditor,
            audit_employee,
        ]
    )

    db.commit()

    for audit in [
        audit_admin,
        audit_manager,
        audit_analyst,
        audit_auditor,
        audit_employee,
    ]:
        db.refresh(audit)

    # ---------------------------------------------------------
    # AUDIT FINDINGS
    # ---------------------------------------------------------

    finding_admin = AuditFinding(
        audit_id=audit_admin.id,
        control_id=control_admin.id,
        title="Admin Finding",
        description="Finding belonging to administrator audit.",
        severity="High",
        recommendation="Remediate the identified issue.",
        status="Open",
    )

    finding_manager = AuditFinding(
        audit_id=audit_manager.id,
        control_id=control_manager.id,
        title="Manager Finding",
        description="Finding belonging to manager audit.",
        severity="Medium",
        recommendation="Remediate the identified issue.",
        status="Open",
    )

    finding_analyst = AuditFinding(
        audit_id=audit_analyst.id,
        control_id=control_analyst.id,
        title="Analyst Finding",
        description="Finding belonging to analyst audit.",
        severity="Medium",
        recommendation="Remediate the identified issue.",
        status="Open",
    )

    finding_auditor = AuditFinding(
        audit_id=audit_auditor.id,
        control_id=control_auditor.id,
        title="Auditor Finding",
        description="Finding belonging to auditor audit.",
        severity="High",
        recommendation="Remediate the identified issue.",
        status="Open",
    )

    finding_employee = AuditFinding(
        audit_id=audit_employee.id,
        control_id=control_employee.id,
        title="Employee Finding",
        description="Finding belonging to employee audit.",
        severity="Low",
        recommendation="Remediate the identified issue.",
        status="Open",
    )

    db.add_all(
        [
            finding_admin,
            finding_manager,
            finding_analyst,
            finding_auditor,
            finding_employee,
        ]
    )

    db.commit()

    for finding in [
        finding_admin,
        finding_manager,
        finding_analyst,
        finding_auditor,
        finding_employee,
    ]:
        db.refresh(finding)

    # ---------------------------------------------------------
    # CORRECTIVE ACTIONS
    # ---------------------------------------------------------

    action_admin = CorrectiveAction(
        finding_id=finding_admin.id,
        assigned_to=admin.id,
        title="Admin Corrective Action",
        description="Corrective action assigned to administrator.",
        priority="High",
        status="Pending",
        due_date=date.today() + timedelta(days=14),
        comments="Administrator remediation.",
    )

    action_manager = CorrectiveAction(
        finding_id=finding_manager.id,
        assigned_to=manager.id,
        title="Manager Corrective Action",
        description="Corrective action assigned to manager.",
        priority="High",
        status="Pending",
        due_date=date.today() + timedelta(days=14),
        comments="Manager remediation.",
    )

    action_analyst = CorrectiveAction(
        finding_id=finding_analyst.id,
        assigned_to=analyst.id,
        title="Analyst Corrective Action",
        description="Corrective action assigned to analyst.",
        priority="Medium",
        status="Pending",
        due_date=date.today() + timedelta(days=14),
        comments="Analyst remediation.",
    )

    action_auditor = CorrectiveAction(
        finding_id=finding_auditor.id,
        assigned_to=auditor.id,
        title="Auditor Corrective Action",
        description="Corrective action assigned to auditor.",
        priority="Medium",
        status="Pending",
        due_date=date.today() + timedelta(days=14),
        comments="Auditor remediation.",
    )

    action_employee = CorrectiveAction(
        finding_id=finding_employee.id,
        assigned_to=employee.id,
        title="Employee Corrective Action",
        description="Corrective action assigned to employee.",
        priority="Low",
        status="Pending",
        due_date=date.today() + timedelta(days=14),
        comments="Employee remediation.",
    )

    db.add_all(
        [
            action_admin,
            action_manager,
            action_analyst,
            action_auditor,
            action_employee,
        ]
    )

    db.commit()

    for action in [
        action_admin,
        action_manager,
        action_analyst,
        action_auditor,
        action_employee,
    ]:
        db.refresh(action)

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
            "manager": control_manager,
            "analyst": control_analyst,
            "auditor": control_auditor,
            "employee": control_employee,
        },
        "evidence": {
            "admin": evidence_admin,
            "manager": evidence_manager,
            "analyst": evidence_analyst,
            "auditor": evidence_auditor,
            "employee": evidence_employee,
        },
        "audits": {
            "admin": audit_admin,
            "manager": audit_manager,
            "analyst": audit_analyst,
            "auditor": audit_auditor,
            "employee": audit_employee,
        },
        "findings": {
            "admin": finding_admin,
            "manager": finding_manager,
            "analyst": finding_analyst,
            "auditor": finding_auditor,
            "employee": finding_employee,
        },
        "corrective_actions": {
            "admin": action_admin,
            "manager": action_manager,
            "analyst": action_analyst,
            "auditor": action_auditor,
            "employee": action_employee,
        },
    }