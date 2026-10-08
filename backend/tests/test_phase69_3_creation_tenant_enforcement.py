from datetime import date, timedelta

import pytest

from app.models.organization import Organization
from app.models.user import User
from app.models.risk import Risk
from app.models.control import Control
from app.models.evidence import Evidence
from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction
from app.models.framework import Framework
from app.auth.hashing import hash_password
from app.core.roles import UserRole


@pytest.fixture()
def second_organization(db):
    organization = Organization(
        name="Phase 69.3 Second Organization",
        slug="phase-69-3-second-organization",
        is_active=True,
    )

    db.add(organization)
    db.flush()

    user = User(
        full_name="Phase 69.3 Second Admin",
        email="phase69-3-admin@example.com",
        hashed_password=hash_password("Password123!"),
        role=UserRole.ADMIN.value,
        manager_id=None,
        department="Executive",
        organization_id=organization.id,
    )

    db.add(user)
    db.commit()

    db.refresh(organization)
    db.refresh(user)

    return {
        "organization": organization,
        "user": user,
    }


def test_risk_creation_assigns_authenticated_user_organization(
    client,
    users,
    auth_headers,
    db,
):
    user = users["admin"]

    response = client.post(
        "/api/v1/risks/",
        headers=auth_headers(user),
        json={
            "title": "Phase 69.3 Tenant Risk",
            "description": "Tenant creation test.",
            "likelihood": 3,
            "impact": 4,
            "owner_id": user.id,
        },
    )

    assert response.status_code == 200

    risk = (
        db.query(Risk)
        .filter(Risk.id == response.json()["id"])
        .first()
    )

    assert risk is not None
    assert risk.organization_id == user.organization_id


def test_control_creation_assigns_authenticated_user_organization(
    client,
    users,
    auth_headers,
    db,
):
    user = users["admin"]

    response = client.post(
        "/api/v1/controls/",
        headers=auth_headers(user),
        json={
            "title": "Phase 69.3 Tenant Control",
            "description": "Tenant creation test.",
            "control_type": "Preventive",
            "status": "Active",
            "effectiveness": 80,
            "owner_id": user.id,
        },
    )

    assert response.status_code == 200

    control = (
        db.query(Control)
        .filter(Control.id == response.json()["id"])
        .first()
    )

    assert control is not None
    assert control.organization_id == user.organization_id


def test_audit_creation_assigns_authenticated_user_organization(
    client,
    users,
    auth_headers,
    db,
):
    user = users["admin"]

    framework = Framework(
        organization_id=user.organization_id,
        name="Phase 69.3 Framework",
        version="1.0",
        description="Tenant test framework.",
    )

    db.add(framework)
    db.commit()
    db.refresh(framework)

    response = client.post(
        "/api/v1/audits/",
        headers=auth_headers(user),
        json={
            "name": "Phase 69.3 Tenant Audit",
            "framework_id": framework.id,
            "auditor_id": user.id,
            "scope": "Tenant creation test",
            "status": "Planned",
            "start_date": date.today().isoformat(),
            "end_date": (
                date.today() + timedelta(days=30)
            ).isoformat(),
        },
    )

    assert response.status_code == 200

    audit = (
        db.query(Audit)
        .filter(Audit.id == response.json()["id"])
        .first()
    )

    assert audit is not None
    assert audit.organization_id == user.organization_id


def test_client_cannot_spoof_risk_organization(
    client,
    users,
    auth_headers,
    second_organization,
    db,
):
    user = users["admin"]
    foreign_org = second_organization["organization"]

    response = client.post(
        "/api/v1/risks/",
        headers=auth_headers(user),
        json={
            "title": "Spoofed Tenant Risk",
            "description": "Organization spoofing test.",
            "likelihood": 2,
            "impact": 2,
            "owner_id": user.id,
            "organization_id": foreign_org.id,
        },
    )

    assert response.status_code == 200

    risk = (
        db.query(Risk)
        .filter(Risk.id == response.json()["id"])
        .first()
    )

    assert risk is not None
    assert risk.organization_id == user.organization_id
    assert risk.organization_id != foreign_org.id


def test_cross_tenant_owner_cannot_be_used_for_risk_creation(
    client,
    users,
    auth_headers,
    second_organization,
):
    user = users["admin"]
    foreign_user = second_organization["user"]

    response = client.post(
        "/api/v1/risks/",
        headers=auth_headers(user),
        json={
            "title": "Cross Tenant Owner Risk",
            "description": "Cross tenant owner test.",
            "likelihood": 3,
            "impact": 3,
            "owner_id": foreign_user.id,
        },
    )

    assert response.status_code in {403, 404}