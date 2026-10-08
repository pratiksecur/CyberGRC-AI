import pytest


def _auth(admin_token):
    return {
        "Authorization": f"Bearer {admin_token}",
    }


def _ids_from_list_response(response):
    assert response.status_code == 200
    data = response.json()

    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get(
            "items",
            data.get("data", []),
        )
    else:
        items = []

    return {
        item["id"]
        for item in items
        if isinstance(item, dict) and "id" in item
    }


# ==========================================================
# DIRECT READ ISOLATION
# ==========================================================


@pytest.mark.parametrize(
    "resource_key,path_template",
    [
        ("risk", "/api/v1/risks/{id}"),
        ("control", "/api/v1/controls/{id}"),
        ("evidence", "/api/v1/evidence/{id}"),
        ("audit", "/api/v1/audits/{id}"),
        ("finding", "/api/v1/audit-findings/{id}"),
        ("corrective_action", "/api/v1/corrective-actions/{id}"),
        ("framework", "/api/v1/frameworks/{id}"),
        ("policy", "/api/v1/policies/{id}"),
        ("framework_control", "/api/v1/framework-controls/{id}"),
        ("business_unit", "/api/v1/enterprise/business-units/{id}"),
        ("department", "/api/v1/enterprise/departments/{id}"),
        ("team", "/api/v1/enterprise/teams/{id}"),
    ],
)
def test_cross_tenant_direct_read_is_blocked(
    client,
    admin_token,
    second_organization_resources,
    resource_key,
    path_template,
):
    resource = second_organization_resources[resource_key]

    response = client.get(
        path_template.format(id=resource.id),
        headers=_auth(admin_token),
    )

    assert response.status_code in {403, 404}


# ==========================================================
# LIST ISOLATION
# ==========================================================


@pytest.mark.parametrize(
    "resource_key,path",
    [
        ("risk", "/api/v1/risks"),
        ("control", "/api/v1/controls"),
        ("evidence", "/api/v1/evidence"),
        ("audit", "/api/v1/audits"),
        ("finding", "/api/v1/audit-findings"),
        ("corrective_action", "/api/v1/corrective-actions"),
        ("framework", "/api/v1/frameworks"),
        ("policy", "/api/v1/policies"),
        ("framework_control", "/api/v1/framework-controls"),
        ("business_unit", "/api/v1/enterprise/business-units"),
        ("department", "/api/v1/enterprise/departments"),
        ("team", "/api/v1/enterprise/teams"),
    ],
)
def test_cross_tenant_list_isolation(
    client,
    admin_token,
    second_organization_resources,
    resource_key,
    path,
):
    foreign_resource = second_organization_resources[resource_key]

    response = client.get(
        path,
        headers=_auth(admin_token),
    )

    returned_ids = _ids_from_list_response(response)

    assert foreign_resource.id not in returned_ids


# ==========================================================
# RISK MUTATION ISOLATION
# ==========================================================


def test_cross_tenant_risk_update_is_blocked(
    client,
    admin_token,
    second_organization_resources,
):
    risk = second_organization_resources["risk"]

    response = client.patch(
        f"/api/v1/risks/{risk.id}",
        headers=_auth(admin_token),
        json={
            "title": "Cross Tenant Attack",
        },
    )

    assert response.status_code in {403, 404, 422}


def test_cross_tenant_risk_delete_is_blocked(
    client,
    admin_token,
    second_organization_resources,
    db,
):
    risk = second_organization_resources["risk"]

    response = client.delete(
        f"/api/v1/risks/{risk.id}",
        headers=_auth(admin_token),
    )

    assert response.status_code in {403, 404}

    remaining = db.query(type(risk)).filter(
        type(risk).id == risk.id
    ).first()

    assert remaining is not None


# ==========================================================
# CONTROL MUTATION ISOLATION
# ==========================================================


def test_cross_tenant_control_update_is_blocked(
    client,
    admin_token,
    second_organization_resources,
):
    control = second_organization_resources["control"]

    response = client.patch(
        f"/api/v1/controls/{control.id}",
        headers=_auth(admin_token),
        json={
            "title": "Cross Tenant Attack",
        },
    )

    assert response.status_code in {403, 404, 422}


def test_cross_tenant_control_delete_is_blocked(
    client,
    admin_token,
    second_organization_resources,
):
    control = second_organization_resources["control"]

    response = client.delete(
        f"/api/v1/controls/{control.id}",
        headers=_auth(admin_token),
    )

    assert response.status_code in {403, 404}


# ==========================================================
# FRAMEWORK + POLICY MUTATION ISOLATION
# ==========================================================


def test_cross_tenant_framework_update_is_blocked(
    client,
    admin_token,
    second_organization_resources,
):
    framework = second_organization_resources["framework"]

    response = client.patch(
        f"/api/v1/frameworks/{framework.id}",
        headers=_auth(admin_token),
        json={
            "name": "Cross Tenant Framework",
        },
    )

    assert response.status_code in {403, 404, 422}


def test_cross_tenant_policy_update_is_blocked(
    client,
    admin_token,
    second_organization_resources,
):
    policy = second_organization_resources["policy"]

    response = client.patch(
        f"/api/v1/policies/{policy.id}",
        headers=_auth(admin_token),
        json={
            "name": "Cross Tenant Policy",
        },
    )

    assert response.status_code in {403, 404, 422}


# ==========================================================
# FRAMEWORK CONTROL ISOLATION
# ==========================================================


def test_cross_tenant_framework_control_update_is_blocked(
    client,
    admin_token,
    second_organization_resources,
):
    framework_control = (
        second_organization_resources["framework_control"]
    )

    response = client.patch(
        f"/api/v1/framework-controls/{framework_control.id}",
        headers=_auth(admin_token),
        json={
            "title": "Cross Tenant Framework Control",
        },
    )

    assert response.status_code in {403, 404, 422}


# ==========================================================
# ENTERPRISE STRUCTURE MUTATION ISOLATION
# ==========================================================


@pytest.mark.parametrize(
    "resource_key,path_template,payload",
    [
        (
            "business_unit",
            "/api/v1/enterprise/business-units/{id}",
            {"name": "Cross Tenant BU"},
        ),
        (
            "department",
            "/api/v1/enterprise/departments/{id}",
            {"name": "Cross Tenant Department"},
        ),
        (
            "team",
            "/api/v1/enterprise/teams/{id}",
            {"name": "Cross Tenant Team"},
        ),
    ],
)
def test_cross_tenant_enterprise_update_is_blocked(
    client,
    admin_token,
    second_organization_resources,
    resource_key,
    path_template,
    payload,
):
    resource = second_organization_resources[resource_key]

    response = client.patch(
        path_template.format(id=resource.id),
        headers=_auth(admin_token),
        json=payload,
    )

    assert response.status_code in {403, 404, 422}
