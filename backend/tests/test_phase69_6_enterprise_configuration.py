from app.models.enterprise_configuration import (
    EnterpriseConfiguration,
)
from app.models.organization import Organization
from app.models.user import User
from app.core.roles import UserRole
from app.auth.hashing import hash_password


def create_foreign_admin(db):

    organization = Organization(
        name="Phase 69.6 Foreign Organization",
        slug="phase-69-6-foreign",
        is_active=True,
    )

    db.add(organization)
    db.flush()

    user = User(
        full_name="Phase 69.6 Foreign Admin",
        email="phase69-6-foreign@example.com",
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


def test_admin_can_get_own_configuration(
    client,
    users,
    auth_headers,
):
    admin = users["admin"]

    response = client.get(
        "/api/v1/enterprise/configuration",
        headers=auth_headers(admin),
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        body["organization_id"]
        == admin.organization_id
    )

    assert body["default_risk_threshold"] == 15
    assert body["critical_risk_threshold"] == 20
    assert (
        body["critical_risk_notification_threshold"]
        == 20
    )


def test_admin_can_update_own_configuration(
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
            "default_risk_threshold": 10,
            "critical_risk_threshold": 20,
            "critical_risk_notification_threshold": 25,
            "ineffective_control_threshold": 45,
            "stale_evidence_days": 60,
            "treatment_stuck_days": 45,
            "treatment_residual_threshold": 12,
            "continuous_risk_reassessment_enabled": True,
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

    assert (
        configuration.default_risk_threshold
        == 10
    )

    assert (
        configuration.critical_risk_threshold
        == 20
    )

    assert (
        configuration.critical_risk_notification_threshold
        == 25
    )

    assert (
        configuration.ineffective_control_threshold
        == 45
    )

    assert (
        configuration.stale_evidence_days
        == 60
    )

    assert (
        configuration.treatment_stuck_days
        == 45
    )

    assert (
        configuration.treatment_residual_threshold
        == 12
    )


def test_configuration_organization_cannot_be_spoofed(
    client,
    users,
    auth_headers,
    db,
):
    admin = users["admin"]

    foreign_org, _ = create_foreign_admin(db)

    response = client.put(
        "/api/v1/enterprise/configuration",
        headers=auth_headers(admin),
        json={
            "organization_id": foreign_org.id,
            "timezone": "Europe/Dublin",
            "default_risk_threshold": 15,
            "critical_risk_threshold": 20,
            "critical_risk_notification_threshold": 20,
            "ineffective_control_threshold": 50,
            "stale_evidence_days": 90,
            "treatment_stuck_days": 30,
            "treatment_residual_threshold": 15,
            "continuous_risk_reassessment_enabled": True,
            "notifications_enabled": True,
            "ai_enabled": True,
        },
    )

    # The schema deliberately ignores no unknown fields here;
    # therefore the spoofed organization_id must be rejected.
    assert response.status_code == 422

    configuration = (
        db.query(EnterpriseConfiguration)
        .filter(
            EnterpriseConfiguration.organization_id
            == admin.organization_id
        )
        .first()
    )

    assert configuration is None


def test_grc_manager_can_view_but_not_modify(
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
            "critical_risk_notification_threshold": 20,
            "ineffective_control_threshold": 50,
            "stale_evidence_days": 90,
            "treatment_stuck_days": 30,
            "treatment_residual_threshold": 15,
            "continuous_risk_reassessment_enabled": True,
            "notifications_enabled": True,
            "ai_enabled": True,
        },
    )

    assert response.status_code == 403


def test_non_management_roles_cannot_access_configuration(
    client,
    users,
    auth_headers,
):
    analyst = users["analyst"]
    auditor = users["auditor"]
    employee = users["employee"]

    for user in (
        analyst,
        auditor,
        employee,
    ):
        response = client.get(
            "/api/v1/enterprise/configuration",
            headers=auth_headers(user),
        )

        assert response.status_code == 403


def test_invalid_threshold_relationship_is_rejected(
    client,
    users,
    auth_headers,
):
    admin = users["admin"]

    response = client.put(
        "/api/v1/enterprise/configuration",
        headers=auth_headers(admin),
        json={
            "timezone": "Europe/Dublin",
            "default_risk_threshold": 30,
            "critical_risk_threshold": 20,
            "critical_risk_notification_threshold": 20,
            "ineffective_control_threshold": 50,
            "stale_evidence_days": 90,
            "treatment_stuck_days": 30,
            "treatment_residual_threshold": 15,
            "continuous_risk_reassessment_enabled": True,
            "notifications_enabled": True,
            "ai_enabled": True,
        },
    )

    assert response.status_code == 422


def test_notification_threshold_cannot_be_lower_than_critical(
    client,
    users,
    auth_headers,
):
    admin = users["admin"]

    response = client.put(
        "/api/v1/enterprise/configuration",
        headers=auth_headers(admin),
        json={
            "timezone": "Europe/Dublin",
            "default_risk_threshold": 15,
            "critical_risk_threshold": 20,
            "critical_risk_notification_threshold": 15,
            "ineffective_control_threshold": 50,
            "stale_evidence_days": 90,
            "treatment_stuck_days": 30,
            "treatment_residual_threshold": 15,
            "continuous_risk_reassessment_enabled": True,
            "notifications_enabled": True,
            "ai_enabled": True,
        },
    )

    assert response.status_code == 422


def test_configuration_isolated_between_tenants(
    client,
    users,
    auth_headers,
    db,
):
    admin = users["admin"]

    foreign_org, foreign_admin = create_foreign_admin(
        db
    )

    response = client.put(
        "/api/v1/enterprise/configuration",
        headers=auth_headers(admin),
        json={
            "timezone": "Europe/Dublin",
            "default_risk_threshold": 10,
            "critical_risk_threshold": 20,
            "critical_risk_notification_threshold": 25,
            "ineffective_control_threshold": 40,
            "stale_evidence_days": 60,
            "treatment_stuck_days": 45,
            "treatment_residual_threshold": 10,
            "continuous_risk_reassessment_enabled": True,
            "notifications_enabled": True,
            "ai_enabled": True,
        },
    )

    assert response.status_code == 200

    response = client.get(
        "/api/v1/enterprise/configuration",
        headers=auth_headers(foreign_admin),
    )

    assert response.status_code == 200

    foreign_configuration = response.json()

    assert (
        foreign_configuration["organization_id"]
        == foreign_org.id
    )

    assert (
        foreign_configuration["default_risk_threshold"]
        == 15
    )

    assert (
        foreign_configuration["critical_risk_notification_threshold"]
        == 20
    )