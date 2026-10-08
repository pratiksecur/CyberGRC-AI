from app.models.business_unit import BusinessUnit
from app.models.department import Department
from app.models.enterprise_configuration import (
    EnterpriseConfiguration,
)
from app.models.grc_team import GrcTeam
from app.models.organization import Organization
from app.models.user import User
from app.core.roles import UserRole
from app.auth.hashing import hash_password


def create_foreign_admin(db):
    organization = Organization(
        name="Phase 69.5 Foreign Organization",
        slug="phase-69-5-foreign",
        is_active=True,
    )

    db.add(organization)
    db.flush()

    user = User(
        full_name="Foreign Admin",
        email="phase69-5-foreign@example.com",
        hashed_password=hash_password(
            "Password123!"
        ),
        role=UserRole.ADMIN.value,
        organization_id=organization.id,
    )

    db.add(user)
    db.commit()

    db.refresh(organization)
    db.refresh(user)

    return organization, user


def test_business_unit_creation_is_tenant_scoped(
    client,
    users,
    auth_headers,
    db,
):
    admin = users["admin"]

    response = client.post(
        "/api/v1/enterprise/business-units",
        headers=auth_headers(admin),
        json={
            "name": "Security",
            "slug": "security",
            "description": "Security business unit",
        },
    )

    assert response.status_code == 200

    business_unit = (
        db.query(BusinessUnit)
        .filter(
            BusinessUnit.id
            == response.json()["id"]
        )
        .first()
    )

    assert business_unit is not None
    assert (
        business_unit.organization_id
        == admin.organization_id
    )


def test_foreign_business_unit_is_not_visible(
    client,
    users,
    auth_headers,
    db,
):
    admin = users["admin"]

    foreign_org, _ = create_foreign_admin(db)

    foreign_business_unit = BusinessUnit(
        organization_id=foreign_org.id,
        name="Foreign BU",
        slug="foreign-bu",
    )

    db.add(foreign_business_unit)
    db.commit()
    db.refresh(foreign_business_unit)

    response = client.get(
        f"/api/v1/enterprise/business-units/{foreign_business_unit.id}",
        headers=auth_headers(admin),
    )

    assert response.status_code == 404


def test_same_business_unit_name_allowed_across_tenants(
    client,
    users,
    auth_headers,
    db,
):
    admin = users["admin"]

    foreign_org, _ = create_foreign_admin(db)

    foreign_business_unit = BusinessUnit(
        organization_id=foreign_org.id,
        name="Shared Name",
        slug="shared-name",
    )

    db.add(foreign_business_unit)
    db.commit()

    response = client.post(
        "/api/v1/enterprise/business-units",
        headers=auth_headers(admin),
        json={
            "name": "Shared Name",
            "slug": "shared-name",
        },
    )

    assert response.status_code == 200


def test_department_must_use_same_tenant_business_unit(
    client,
    users,
    auth_headers,
    db,
):
    admin = users["admin"]

    foreign_org, _ = create_foreign_admin(db)

    foreign_business_unit = BusinessUnit(
        organization_id=foreign_org.id,
        name="Foreign BU",
        slug="foreign-bu",
    )

    db.add(foreign_business_unit)
    db.commit()
    db.refresh(foreign_business_unit)

    response = client.post(
        "/api/v1/enterprise/departments",
        headers=auth_headers(admin),
        json={
            "business_unit_id": foreign_business_unit.id,
            "name": "Foreign Department",
            "slug": "foreign-department",
        },
    )

    assert response.status_code == 403


def test_team_relationships_must_be_same_tenant(
    client,
    users,
    auth_headers,
    db,
):
    admin = users["admin"]

    foreign_org, _ = create_foreign_admin(db)

    foreign_business_unit = BusinessUnit(
        organization_id=foreign_org.id,
        name="Foreign BU",
        slug="foreign-bu",
    )

    db.add(foreign_business_unit)
    db.commit()
    db.refresh(foreign_business_unit)

    response = client.post(
        "/api/v1/enterprise/teams",
        headers=auth_headers(admin),
        json={
            "name": "Foreign Team",
            "slug": "foreign-team",
            "business_unit_id": foreign_business_unit.id,
        },
    )

    assert response.status_code == 403


def test_user_structure_cannot_use_foreign_team(
    client,
    users,
    auth_headers,
    db,
):
    admin = users["admin"]

    foreign_org, _ = create_foreign_admin(db)

    foreign_team = GrcTeam(
        organization_id=foreign_org.id,
        name="Foreign Team",
        slug="foreign-team",
    )

    db.add(foreign_team)
    db.commit()
    db.refresh(foreign_team)

    response = client.patch(
        f"/api/v1/enterprise/users/{admin.id}/structure",
        headers=auth_headers(admin),
        json={
            "team_id": foreign_team.id,
        },
    )

    assert response.status_code == 403


def test_user_structure_assignment(
    client,
    users,
    auth_headers,
    db,
):
    admin = users["admin"]

    business_unit = BusinessUnit(
        organization_id=admin.organization_id,
        name="Operations",
        slug="operations",
    )

    db.add(business_unit)
    db.flush()

    department = Department(
        organization_id=admin.organization_id,
        business_unit_id=business_unit.id,
        name="Compliance",
        slug="compliance",
    )

    db.add(department)
    db.flush()

    team = GrcTeam(
        organization_id=admin.organization_id,
        business_unit_id=business_unit.id,
        department_id=department.id,
        name="Compliance Team",
        slug="compliance-team",
    )

    db.add(team)
    db.commit()

    response = client.patch(
        f"/api/v1/enterprise/users/{admin.id}/structure",
        headers=auth_headers(admin),
        json={
            "business_unit_id": business_unit.id,
            "department_id": department.id,
            "team_id": team.id,
        },
    )

    assert response.status_code == 200

    db.refresh(admin)

    assert (
        admin.business_unit_id
        == business_unit.id
    )

    assert (
        admin.department_id
        == department.id
    )

    assert (
        admin.team_id
        == team.id
    )

    assert admin.department == "Compliance"


def test_enterprise_configuration_is_tenant_scoped(
    client,
    users,
    auth_headers,
    db,
):
    admin = users["admin"]

    response = client.put(
        "/api/v1/enterprise/configuration",
        headers=auth_headers(admin),
        json={
            "timezone": "Europe/Dublin",
            "default_risk_threshold": 15,
            "critical_risk_threshold": 20,
            "stale_evidence_days": 120,
            "treatment_stuck_days": 45,
            "notifications_enabled": True,
            "ai_enabled": True,
        },
    )

    assert response.status_code == 200

    configuration = (
        db.query(EnterpriseConfiguration)
        .filter(
            EnterpriseConfiguration.organization_id
            == admin.organization_id
        )
        .first()
    )

    assert configuration is not None
    assert configuration.timezone == "Europe/Dublin"
    assert configuration.stale_evidence_days == 120
    assert configuration.treatment_stuck_days == 45


def test_grc_manager_can_view_but_not_modify_configuration(
    client,
    users,
    auth_headers,
):
    manager = users["manager"]

    response = client.get(
        "/api/v1/enterprise/configuration",
        headers=auth_headers(manager),
    )

    assert response.status_code == 200

    response = client.put(
        "/api/v1/enterprise/configuration",
        headers=auth_headers(manager),
        json={
            "timezone": "Europe/Dublin",
            "default_risk_threshold": 15,
            "critical_risk_threshold": 20,
            "stale_evidence_days": 90,
            "treatment_stuck_days": 30,
            "notifications_enabled": True,
            "ai_enabled": True,
        },
    )

    assert response.status_code == 403