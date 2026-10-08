from datetime import date

from app.models.framework import Framework
from app.models.organization import Organization
from app.models.policy import Policy
from app.models.user import User


def test_framework_create_is_tenant_owned(
    client,
    auth_headers,
    users,
):
    response = client.post(
        "/api/v1/frameworks/",
        json={
            "name": "Tenant ISO Framework",
            "version": "2026",
            "description": "Tenant-specific compliance framework.",
        },
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["organization_id"] == users["admin"].organization_id


def test_framework_rejects_organization_spoofing(
    client,
    auth_headers,
    users,
):
    response = client.post(
        "/api/v1/frameworks/",
        json={
            "organization_id": 999999,
            "name": "Spoofed Framework",
            "version": "1.0",
            "description": "This organization must not be accepted.",
        },
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 422


def test_policy_create_is_tenant_owned(
    client,
    auth_headers,
    users,
):
    response = client.post(
        "/api/v1/policies/",
        json={
            "owner_id": users["admin"].id,
            "name": "Information Security Policy",
            "version": "1.0",
            "description": "Organization information security policy.",
            "status": "Draft",
            "effective_date": "2026-10-01",
            "review_date": "2027-10-01",
        },
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["organization_id"] == users["admin"].organization_id
    assert data["owner_id"] == users["admin"].id


def test_policy_rejects_organization_spoofing(
    client,
    auth_headers,
    users,
):
    response = client.post(
        "/api/v1/policies/",
        json={
            "organization_id": 999999,
            "owner_id": users["admin"].id,
            "name": "Spoofed Policy",
            "version": "1.0",
            "description": "This organization must not be accepted.",
        },
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 422


def test_policy_owner_must_be_same_tenant(
    client,
    auth_headers,
    users,
    db,
):
    other_org = Organization(
        name="Other Test Organization",
        slug="other-test-organization",
    )

    db.add(other_org)
    db.commit()
    db.refresh(other_org)

    foreign_user = User(
        full_name="Foreign User",
        email="foreign-policy-owner@example.com",
        hashed_password=users["admin"].hashed_password,
        role="Employee",
        organization_id=other_org.id,
    )

    db.add(foreign_user)
    db.commit()
    db.refresh(foreign_user)

    response = client.post(
        "/api/v1/policies/",
        json={
            "owner_id": foreign_user.id,
            "name": "Foreign Owner Policy",
            "version": "1.0",
            "description": "This policy must reject a foreign owner.",
        },
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 404


def test_policy_dates_are_validated(
    client,
    auth_headers,
    users,
):
    response = client.post(
        "/api/v1/policies/",
        json={
            "owner_id": users["admin"].id,
            "name": "Invalid Policy Dates",
            "version": "1.0",
            "description": "Policy with invalid date ordering.",
            "effective_date": "2027-01-01",
            "review_date": "2026-01-01",
        },
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 422


def test_auditor_can_view_policies(
    client,
    auth_headers,
    users,
):
    response = client.get(
        "/api/v1/policies/",
        headers=auth_headers(users["auditor"]),
    )

    assert response.status_code == 200


def test_employee_cannot_create_policy(
    client,
    auth_headers,
    users,
):
    response = client.post(
        "/api/v1/policies/",
        json={
            "owner_id": users["employee"].id,
            "name": "Employee Policy",
            "version": "1.0",
            "description": "Employee should not create policies.",
        },
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 403


def test_employee_can_view_policies(
    client,
    auth_headers,
    users,
):
    response = client.get(
        "/api/v1/policies/",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 200


def test_frameworks_are_organization_scoped(
    client,
    auth_headers,
    users,
    db,
):
    framework = Framework(
        organization_id=users["admin"].organization_id,
        name="Organization Scoped Framework",
        version="1.0",
        description="Framework belonging to the organization.",
    )

    db.add(framework)
    db.commit()
    db.refresh(framework)

    response = client.get(
        f"/api/v1/frameworks/{framework.id}",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200
    assert response.json()["organization_id"] == (
        users["admin"].organization_id
    )