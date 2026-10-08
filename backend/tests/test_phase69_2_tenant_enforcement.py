from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

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
        name="Second Organization",
        slug="second-organization",
        is_active=True,
    )

    db.add(organization)
    db.flush()

    user = User(
        full_name="Second Organization Admin",
        email="second-admin@example.com",
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


@pytest.fixture()
def cross_tenant_resources(
    db,
    resource_data,
    second_organization,
):
    organization = second_organization["organization"]
    user = second_organization["user"]

    framework = Framework(
        organization_id=organization.id,
        name="Second Organization Framework",
        version="1.0",
        description="Cross-tenant isolation test framework.",
    )

    db.add(framework)
    db.flush()

    risk = Risk(
        title="Second Organization Risk",
        description="Cross-tenant risk.",
        likelihood=3,
        impact=3,
        risk_score=9,
        status="Open",
        owner_id=user.id,
        created_by_id=user.id,
        organization_id=organization.id,
    )

    control = Control(
        title="Second Organization Control",
        description="Cross-tenant control.",
        control_type="Preventive",
        status="Active",
        effectiveness=80,
        owner_id=user.id,
        created_by_id=user.id,
        organization_id=organization.id,
    )

    db.add_all([risk, control])
    db.flush()

    evidence = Evidence(
        title="Second Organization Evidence",
        description="Cross-tenant evidence.",
        control_id=control.id,
        file_name="cross-tenant.pdf",
        file_path="/test/cross-tenant.pdf",
        uploaded_by=user.id,
        organization_id=organization.id,
    )

    audit = Audit(
        name="Second Organization Audit",
        framework_id=framework.id,
        auditor_id=user.id,
        created_by_id=user.id,
        scope="Second Organization",
        status="Planned",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30),
        organization_id=organization.id,
    )

    db.add_all([evidence, audit])
    db.flush()

    finding = AuditFinding(
        audit_id=audit.id,
        control_id=control.id,
        title="Second Organization Finding",
        description="Cross-tenant finding.",
        severity="High",
        recommendation="Remediate.",
        status="Open",
        organization_id=organization.id,
    )

    db.add(finding)
    db.flush()

    action = CorrectiveAction(
        finding_id=finding.id,
        assigned_to=user.id,
        title="Second Organization Action",
        description="Cross-tenant corrective action.",
        priority="High",
        status="Pending",
        due_date=date.today() + timedelta(days=14),
        comments="Cross-tenant test.",
        organization_id=organization.id,
    )

    db.add(action)
    db.commit()

    for resource in [
        risk,
        control,
        evidence,
        audit,
        finding,
        action,
    ]:
        db.refresh(resource)

    return {
        "risk": risk,
        "control": control,
        "evidence": evidence,
        "audit": audit,
        "finding": finding,
        "action": action,
    }


def test_cross_tenant_resources_are_not_visible(
    client,
    users,
    auth_headers,
    cross_tenant_resources,
):
    headers = auth_headers(users["admin"])

    resources = cross_tenant_resources

    endpoints = [
        f"/api/v1/risks/{resources['risk'].id}",
        f"/api/v1/controls/{resources['control'].id}",
        f"/api/v1/evidence/{resources['evidence'].id}",
        f"/api/v1/audits/{resources['audit'].id}",
        f"/api/v1/audit-findings/{resources['finding'].id}",
        f"/api/v1/corrective-actions/{resources['action'].id}",
    ]

    for endpoint in endpoints:
        response = client.get(
            endpoint,
            headers=headers,
        )

        assert response.status_code == 404, (
            f"{endpoint} returned "
            f"{response.status_code} instead of 404"
        )


def test_cross_tenant_resources_are_not_listed(
    client,
    users,
    auth_headers,
    cross_tenant_resources,
):
    headers = auth_headers(users["admin"])

    endpoints = [
        "/api/v1/risks/",
        "/api/v1/controls/",
        "/api/v1/evidence/",
        "/api/v1/audits/",
        "/api/v1/audit-findings/",
        "/api/v1/corrective-actions/",
    ]

    forbidden_ids = {
        resource.id
        for resource in cross_tenant_resources.values()
    }

    for endpoint in endpoints:
        response = client.get(
            endpoint,
            headers=headers,
        )

        assert response.status_code == 200

        payload = response.json()

        returned_ids = {
            item["id"]
            for item in payload
        }

        assert returned_ids.isdisjoint(forbidden_ids)


def test_cross_tenant_resources_cannot_be_modified(
    client,
    users,
    auth_headers,
    cross_tenant_resources,
):
    headers = auth_headers(users["admin"])

    risk = cross_tenant_resources["risk"]

    response = client.patch(
        f"/api/v1/risks/{risk.id}",
        headers=headers,
        json={
            "title": "Attempted Cross Tenant Update",
        },
    )

    assert response.status_code == 404


def test_cross_tenant_resources_cannot_be_deleted(
    client,
    users,
    auth_headers,
    cross_tenant_resources,
):
    headers = auth_headers(users["admin"])

    control = cross_tenant_resources["control"]

    response = client.delete(
        f"/api/v1/controls/{control.id}",
        headers=headers,
    )

    assert response.status_code == 404


def test_cross_tenant_resource_relationships_are_consistent(
    cross_tenant_resources,
    second_organization,
):
    organization_id = second_organization["organization"].id

    for resource in cross_tenant_resources.values():
        assert resource.organization_id == organization_id