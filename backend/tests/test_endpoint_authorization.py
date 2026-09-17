import pytest


# ==========================================================
# BASIC AUTHENTICATION TESTS
# ==========================================================

@pytest.mark.parametrize(
    "user_key",
    [
        "admin",
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_each_role_can_authenticate_against_api(
    client,
    users,
    auth_headers,
    user_key,
):
    """
    Every supported role must be able to authenticate through
    the real FastAPI authentication dependency.
    """

    user = users[user_key]

    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers(user),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user.id
    assert data["email"] == user.email
    assert data["role"] == user.role


def test_protected_endpoint_rejects_missing_token(
    client,
):
    """
    Protected API endpoints must reject requests that do not
    contain an authentication token.
    """

    response = client.get(
        "/api/v1/risks/",
    )

    assert response.status_code == 401


def test_protected_endpoint_rejects_invalid_token(
    client,
):
    """
    Protected API endpoints must reject malformed or invalid
    JWTs.
    """

    response = client.get(
        "/api/v1/risks/",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


# ==========================================================
# RISK — ORGANIZATIONAL VISIBILITY
# ==========================================================

def test_admin_can_access_all_risks(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    Admin has organization-wide Risk visibility.
    """

    response = client.get(
        "/api/v1/risks/",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200

    risk_ids = {
        risk["id"]
        for risk in response.json()
    }

    expected_ids = {
        resource_data["risks"]["admin"].id,
        resource_data["risks"]["manager"].id,
        resource_data["risks"]["analyst"].id,
        resource_data["risks"]["auditor"].id,
        resource_data["risks"]["employee"].id,
    }

    assert risk_ids == expected_ids


def test_grc_manager_can_access_manager_and_subordinate_risks(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    GRC Manager has visibility over itself and its
    organizational descendants.
    """

    response = client.get(
        "/api/v1/risks/",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    risk_ids = {
        risk["id"]
        for risk in response.json()
    }

    assert resource_data["risks"]["manager"].id in risk_ids
    assert resource_data["risks"]["analyst"].id in risk_ids
    assert resource_data["risks"]["auditor"].id in risk_ids
    assert resource_data["risks"]["employee"].id in risk_ids

    assert resource_data["risks"]["admin"].id not in risk_ids


def test_risk_analyst_can_access_only_own_risks(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    Risk Analyst has own-resource Risk visibility.
    """

    response = client.get(
        "/api/v1/risks/",
        headers=auth_headers(users["analyst"]),
    )

    assert response.status_code == 200

    risk_ids = {
        risk["id"]
        for risk in response.json()
    }

    assert risk_ids == {
        resource_data["risks"]["analyst"].id
    }


def test_auditor_can_access_all_risks(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    Auditor has organization-wide Risk visibility.
    """

    response = client.get(
        "/api/v1/risks/",
        headers=auth_headers(users["auditor"]),
    )

    assert response.status_code == 200

    risk_ids = {
        risk["id"]
        for risk in response.json()
    }

    expected_ids = {
        resource_data["risks"]["admin"].id,
        resource_data["risks"]["manager"].id,
        resource_data["risks"]["analyst"].id,
        resource_data["risks"]["auditor"].id,
        resource_data["risks"]["employee"].id,
    }

    assert risk_ids == expected_ids


def test_employee_can_access_only_own_risks(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    Employee has own-resource Risk visibility.
    """

    response = client.get(
        "/api/v1/risks/",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 200

    risk_ids = {
        risk["id"]
        for risk in response.json()
    }

    assert risk_ids == {
        resource_data["risks"]["employee"].id
    }


# ==========================================================
# RISK — OBJECT LEVEL VISIBILITY
# ==========================================================

@pytest.mark.parametrize(
    "user_key,risk_owner_key,expected_status",
    [
        ("admin", "admin", 200),
        ("admin", "manager", 200),
        ("admin", "analyst", 200),
        ("admin", "auditor", 200),
        ("admin", "employee", 200),

        ("manager", "manager", 200),
        ("manager", "analyst", 200),
        ("manager", "auditor", 200),
        ("manager", "employee", 200),
        ("manager", "admin", 404),

        ("analyst", "analyst", 200),
        ("analyst", "admin", 404),
        ("analyst", "manager", 404),
        ("analyst", "auditor", 404),
        ("analyst", "employee", 404),

        ("auditor", "admin", 200),
        ("auditor", "manager", 200),
        ("auditor", "analyst", 200),
        ("auditor", "auditor", 200),
        ("auditor", "employee", 200),

        ("employee", "employee", 200),
        ("employee", "admin", 404),
        ("employee", "manager", 404),
        ("employee", "analyst", 404),
        ("employee", "auditor", 404),
    ],
)
def test_risk_object_visibility_matrix(
    client,
    users,
    resource_data,
    auth_headers,
    user_key,
    risk_owner_key,
    expected_status,
):
    """
    Verify object-level Risk visibility for every role/scope
    combination in the authorization matrix.
    """

    risk = resource_data["risks"][risk_owner_key]

    response = client.get(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == expected_status


# ==========================================================
# RISK — UNAUTHORIZED MUTATION
# ==========================================================

@pytest.mark.parametrize(
    "user_key,risk_owner_key",
    [
        ("manager", "admin"),
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("analyst", "auditor"),
        ("analyst", "employee"),
        ("employee", "admin"),
        ("employee", "manager"),
        ("employee", "analyst"),
        ("employee", "auditor"),
    ],
)
def test_users_cannot_update_risks_outside_scope(
    client,
    users,
    resource_data,
    auth_headers,
    user_key,
    risk_owner_key,
):
    """
    Users must not be able to update Risks outside their
    configured resource visibility scope.
    """

    risk = resource_data["risks"][risk_owner_key]

    response = client.patch(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users[user_key]),
        json={
            "title": "Unauthorized Risk Update",
        },
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "user_key,risk_owner_key",
    [
        ("admin", "admin"),
        ("admin", "manager"),
        ("admin", "analyst"),
        ("admin", "auditor"),
        ("admin", "employee"),

        ("manager", "manager"),
        ("manager", "analyst"),
        ("manager", "auditor"),
        ("manager", "employee"),

        ("analyst", "analyst"),

        ("employee", "employee"),
    ],
)
def test_users_can_update_risks_within_scope(
    client,
    users,
    resource_data,
    auth_headers,
    user_key,
    risk_owner_key,
):
    """
    Users with Risk update permission and sufficient resource
    scope may update an accessible Risk.
    """

    risk = resource_data["risks"][risk_owner_key]

    response = client.patch(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users[user_key]),
        json={
            "title": f"Authorized update by {user_key}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == risk.id
    assert data["title"] == f"Authorized update by {user_key}"


# ==========================================================
# RISK — CREATE / OWNER SCOPE
# ==========================================================

@pytest.mark.parametrize(
    "user_key,owner_key,expected_status",
    [
        ("admin", "admin", 200),
        ("admin", "manager", 200),
        ("admin", "analyst", 200),
        ("admin", "auditor", 200),
        ("admin", "employee", 200),

        ("manager", "manager", 200),
        ("manager", "analyst", 200),
        ("manager", "auditor", 200),
        ("manager", "employee", 200),
        ("manager", "admin", 403),

        ("analyst", "analyst", 200),
        ("analyst", "admin", 403),
        ("analyst", "manager", 403),
        ("analyst", "auditor", 403),
        ("analyst", "employee", 403),

        ("employee", "employee", 200),
        ("employee", "admin", 403),
        ("employee", "manager", 403),
        ("employee", "analyst", 403),
        ("employee", "auditor", 403),
    ],
)
def test_risk_creation_owner_scope(
    client,
    users,
    auth_headers,
    user_key,
    owner_key,
    expected_status,
):
    """
    Creating a Risk for another user must respect the creator's
    resource ownership scope.

    This is especially important because a user should not be
    able to create a resource and assign it to an out-of-scope
    owner.
    """

    response = client.post(
        "/api/v1/risks/",
        headers=auth_headers(users[user_key]),
        json={
            "title": f"Scope test risk {user_key}-{owner_key}",
            "description": "Authorization scope test.",
            "likelihood": 2,
            "impact": 3,
            "owner_id": users[owner_key].id,
        },
    )

    assert response.status_code == expected_status

    if expected_status == 200:
        data = response.json()

        assert data["owner_id"] == users[owner_key].id


# ==========================================================
# RISK — DELETE AUTHORIZATION
# ==========================================================

@pytest.mark.parametrize(
    "user_key,risk_owner_key,expected_status",
    [
        # Admin has risks:delete permission and organization-wide
        # Risk visibility.
        ("admin", "admin", 200),

        # These roles do not have risks:delete permission.
        # Therefore the permission check correctly returns 403
        # before resource-level visibility can be evaluated.
        ("manager", "admin", 403),
        ("analyst", "admin", 403),
        ("auditor", "admin", 403),
        ("employee", "admin", 403),
    ],
)
def test_risk_delete_respects_permission_and_scope(
    client,
    users,
    resource_data,
    auth_headers,
    user_key,
    risk_owner_key,
    expected_status,
):
    """
    Delete operations must respect the configured Risk delete
    permission.

    Admin is authorized to delete Risks.

    GRC Manager, Risk Analyst, Auditor, and Employee do not have
    risks:delete permission, so their requests must be rejected
    with HTTP 403.

    Because only Admin currently has Risk delete permission, this
    test cannot independently exercise restricted-scope deletion.
    If delete permission is later granted to a restricted role,
    additional scope-specific delete cases should be added.
    """

    risk = resource_data["risks"][risk_owner_key]

    response = client.delete(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == expected_status


# ==========================================================
# RISK-CONTROL MAPPING — CREATE AUTHORIZATION
# ==========================================================

def test_risk_analyst_can_create_mapping_for_own_risk_and_control(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    Risk Analyst may create a mapping when both the Risk and
    Control are within the Analyst's mapping visibility scope.
    """

    response = client.post(
        "/api/v1/risk-controls/",
        headers=auth_headers(users["analyst"]),
        json={
            "risk_id": resource_data["risks"]["analyst"].id,
            "control_id": resource_data["controls"]["analyst"].id,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_id"] == resource_data["risks"]["analyst"].id
    assert data["control_id"] == resource_data["controls"]["analyst"].id


@pytest.mark.parametrize(
    "risk_owner_key,control_owner_key",
    [
        ("admin", "analyst"),
        ("manager", "analyst"),
        ("auditor", "analyst"),
        ("employee", "analyst"),
        ("analyst", "admin"),
        ("analyst", "employee"),
    ],
)
def test_risk_analyst_cannot_create_mapping_with_out_of_scope_resource(
    client,
    users,
    resource_data,
    auth_headers,
    risk_owner_key,
    control_owner_key,
):
    """
    Risk Analyst must not be able to create a Risk-Control
    mapping when either side of the relationship is outside
    the Analyst's configured mapping scope.
    """

    response = client.post(
        "/api/v1/risk-controls/",
        headers=auth_headers(users["analyst"]),
        json={
            "risk_id": resource_data["risks"][risk_owner_key].id,
            "control_id": resource_data["controls"][control_owner_key].id,
        },
    )

    assert response.status_code == 403


def test_employee_cannot_create_risk_control_mapping(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    Employee does not have create permission for
    control_framework_mappings.
    """

    response = client.post(
        "/api/v1/risk-controls/",
        headers=auth_headers(users["employee"]),
        json={
            "risk_id": resource_data["risks"]["employee"].id,
            "control_id": resource_data["controls"]["employee"].id,
        },
    )

    assert response.status_code == 403


# ==========================================================
# RISK-CONTROL MAPPING — READ / BOLA PROTECTION
# ==========================================================

def test_risk_analyst_can_view_mappings_for_own_risk(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    Analyst can query mappings belonging to the Analyst's own
    Risk.
    """

    response = client.get(
        f"/api/v1/risk-controls/risk/"
        f"{resource_data['risks']['analyst'].id}",
        headers=auth_headers(users["analyst"]),
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "risk_owner_key",
    [
        "admin",
        "manager",
        "auditor",
        "employee",
    ],
)
def test_risk_analyst_cannot_view_mappings_for_other_users_risks(
    client,
    users,
    resource_data,
    auth_headers,
    risk_owner_key,
):
    """
    Changing the risk_id must not allow an Analyst to enumerate
    controls attached to another user's Risk.

    The endpoint intentionally returns 404 so the existence of
    the protected Risk is not disclosed.
    """

    response = client.get(
        f"/api/v1/risk-controls/risk/"
        f"{resource_data['risks'][risk_owner_key].id}",
        headers=auth_headers(users["analyst"]),
    )

    assert response.status_code == 404


def test_risk_analyst_can_view_mappings_for_own_control(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    Analyst can query mappings belonging to the Analyst's own
    Control.
    """

    response = client.get(
        f"/api/v1/risk-controls/control/"
        f"{resource_data['controls']['analyst'].id}",
        headers=auth_headers(users["analyst"]),
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "control_owner_key",
    [
        "admin",
        "employee",
    ],
)
def test_risk_analyst_cannot_view_mappings_for_other_users_controls(
    client,
    users,
    resource_data,
    auth_headers,
    control_owner_key,
):
    """
    Changing the control_id must not allow an Analyst to
    enumerate Risks attached to another user's Control.

    The endpoint intentionally returns 404 so the existence of
    the protected Control is not disclosed.
    """

    response = client.get(
        f"/api/v1/risk-controls/control/"
        f"{resource_data['controls'][control_owner_key].id}",
        headers=auth_headers(users["analyst"]),
    )

    assert response.status_code == 404


# ==========================================================
# RISK-CONTROL MAPPING — MANAGER / AUDITOR VISIBILITY
# ==========================================================

@pytest.mark.parametrize(
    "risk_owner_key",
    [
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_grc_manager_can_view_mappings_for_manager_and_subordinates(
    client,
    users,
    resource_data,
    auth_headers,
    risk_owner_key,
):
    """
    GRC Manager has mapping visibility over manager-owned
    and subordinate-owned Risks.
    """

    response = client.get(
        f"/api/v1/risk-controls/risk/"
        f"{resource_data['risks'][risk_owner_key].id}",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200


def test_grc_manager_cannot_view_admin_risk_mappings(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    GRC Manager must not access mapping data associated with
    the Admin because the Admin is outside the Manager's
    organizational subtree.
    """

    response = client.get(
        f"/api/v1/risk-controls/risk/"
        f"{resource_data['risks']['admin'].id}",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "risk_owner_key",
    [
        "admin",
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_auditor_can_view_mappings_for_all_risks(
    client,
    users,
    resource_data,
    auth_headers,
    risk_owner_key,
):
    """
    Auditor has organization-wide mapping visibility.
    """

    response = client.get(
        f"/api/v1/risk-controls/risk/"
        f"{resource_data['risks'][risk_owner_key].id}",
        headers=auth_headers(users["auditor"]),
    )

    assert response.status_code == 200


def test_employee_can_view_risk_control_mappings(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    Employee has organization-wide view permission for
    control-framework mappings.

    Although Employee has own-resource visibility for Risks,
    the mapping resource itself is configured with
    organization-wide visibility.

    Therefore Employee may view Risk-Control mapping data.
    """

    response = client.get(
        f"/api/v1/risk-controls/risk/"
        f"{resource_data['risks']['employee'].id}",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 200


# ==========================================================
# RISK-CONTROL MAPPING — DELETE / BOLA PROTECTION
# ==========================================================

def test_admin_can_delete_risk_control_mapping(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    """
    Admin has organization-wide visibility and mapping-delete
    permission, so Admin may remove an existing mapping.
    """

    from app.models.risk_control import RiskControl

    mapping = RiskControl(
        risk_id=resource_data["risks"]["employee"].id,
        control_id=resource_data["controls"]["employee"].id,
    )

    db.add(mapping)
    db.commit()
    db.refresh(mapping)

    response = client.delete(
        f"/api/v1/risk-controls/{mapping.id}",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200

    assert db.query(RiskControl).filter(
        RiskControl.id == mapping.id
    ).first() is None


def test_grc_manager_cannot_delete_admin_mapping(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    """
    GRC Manager has mapping-delete permission but the Admin's
    Risk is outside the Manager's organizational scope.

    The endpoint must therefore hide the mapping with 404.
    """

    from app.models.risk_control import RiskControl

    mapping = RiskControl(
        risk_id=resource_data["risks"]["admin"].id,
        control_id=resource_data["controls"]["analyst"].id,
    )

    db.add(mapping)
    db.commit()
    db.refresh(mapping)

    response = client.delete(
        f"/api/v1/risk-controls/{mapping.id}",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 404

    assert db.query(RiskControl).filter(
        RiskControl.id == mapping.id
    ).first() is not None


def test_grc_manager_can_delete_subordinate_mapping(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    """
    GRC Manager may delete a mapping when both associated
    resources are within the Manager's organizational scope.
    """

    from app.models.risk_control import RiskControl

    mapping = RiskControl(
        risk_id=resource_data["risks"]["analyst"].id,
        control_id=resource_data["controls"]["analyst"].id,
    )

    db.add(mapping)
    db.commit()
    db.refresh(mapping)

    response = client.delete(
        f"/api/v1/risk-controls/{mapping.id}",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    assert db.query(RiskControl).filter(
        RiskControl.id == mapping.id
    ).first() is None


def test_risk_analyst_cannot_delete_mapping(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    """
    Risk Analyst does not have mapping-delete permission.
    """

    from app.models.risk_control import RiskControl

    mapping = RiskControl(
        risk_id=resource_data["risks"]["analyst"].id,
        control_id=resource_data["controls"]["analyst"].id,
    )

    db.add(mapping)
    db.commit()
    db.refresh(mapping)

    response = client.delete(
        f"/api/v1/risk-controls/{mapping.id}",
        headers=auth_headers(users["analyst"]),
    )

    assert response.status_code == 403

    assert db.query(RiskControl).filter(
        RiskControl.id == mapping.id
    ).first() is not None


def test_employee_cannot_delete_mapping(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    """
    Employee does not have mapping-delete permission.
    """

    from app.models.risk_control import RiskControl

    mapping = RiskControl(
        risk_id=resource_data["risks"]["employee"].id,
        control_id=resource_data["controls"]["employee"].id,
    )

    db.add(mapping)
    db.commit()
    db.refresh(mapping)

    response = client.delete(
        f"/api/v1/risk-controls/{mapping.id}",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 403

    assert db.query(RiskControl).filter(
        RiskControl.id == mapping.id
    ).first() is not None


def test_mapping_delete_hides_nonexistent_mapping(
    client,
    users,
    auth_headers,
):
    """
    Deleting a mapping that does not exist must return 404.
    """

    response = client.delete(
        "/api/v1/risk-controls/999999",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 404

# ==========================================================
# CORRECTIVE ACTION REPORT — AUTHORIZATION / BOLA PROTECTION
# ==========================================================

def test_admin_can_view_all_corrective_action_reports(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    Admin has organization-wide reports:view permission,
    so the corrective-action report may contain actions
    assigned to any user.
    """

    response = client.get(
        "/api/v1/reports/corrective-actions/",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200


def test_grc_manager_can_view_subordinate_corrective_action_report(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    GRC Manager has reports:view with subordinate scope.
    """

    response = client.get(
        "/api/v1/reports/corrective-actions/",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert "summary" in data
    assert "actions" in data


def test_risk_analyst_can_view_own_corrective_action_report(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    Risk Analyst has reports:view with OWN scope.
    """

    response = client.get(
        "/api/v1/reports/corrective-actions/",
        headers=auth_headers(users["analyst"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert "summary" in data
    assert "actions" in data


def test_auditor_can_view_all_corrective_action_reports(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    Auditor has organization-wide reports:view permission.
    """

    response = client.get(
        "/api/v1/reports/corrective-actions/",
        headers=auth_headers(users["auditor"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert "summary" in data
    assert "actions" in data


def test_employee_cannot_view_corrective_action_report(
    client,
    users,
    auth_headers,
):
    """
    Employee does not have reports:view permission.
    """

    response = client.get(
        "/api/v1/reports/corrective-actions/",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 403