def test_admin_can_access_audit_assurance(
    client,
    users,
    auth_headers,
):
    response = client.get(
        "/api/v1/intelligence/audit-assurance",
        headers=auth_headers(
            users["admin"]
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert "portfolio" in body
    assert "planning" in body
    assert "testing" in body
    assert "evidence" in body
    assert "remediation" in body
    assert "closure" in body
    assert "assurance_signals" in body
    assert "audits" in body
    assert "scope" in body


def test_manager_can_access_audit_assurance(
    client,
    users,
    auth_headers,
):
    response = client.get(
        "/api/v1/intelligence/audit-assurance",
        headers=auth_headers(
            users["manager"]
        ),
    )

    assert response.status_code == 200


def test_risk_analyst_can_access_audit_assurance(
    client,
    users,
    auth_headers,
):
    response = client.get(
        "/api/v1/intelligence/audit-assurance",
        headers=auth_headers(
            users["analyst"]
        ),
    )

    assert response.status_code == 200


def test_auditor_can_access_audit_assurance(
    client,
    users,
    auth_headers,
):
    response = client.get(
        "/api/v1/intelligence/audit-assurance",
        headers=auth_headers(
            users["auditor"]
        ),
    )

    assert response.status_code == 200


def test_employee_can_access_organization_audit_assurance(
    client,
    users,
    auth_headers,
    resource_data,
):
    response = client.get(
        "/api/v1/intelligence/audit-assurance",
        headers=auth_headers(
            users["employee"]
        ),
    )

    assert response.status_code == 200

    body = response.json()

    expected_audit_count = len(
        resource_data[
            "audits"
        ]
    )

    assert (
        body[
            "scope"
        ]["audit_count"]
        == expected_audit_count
    )


def test_unauthenticated_cannot_access_audit_assurance(
    client,
):
    response = client.get(
        "/api/v1/intelligence/audit-assurance"
    )

    assert response.status_code == 401


def test_audit_assurance_endpoint_is_read_only(
    client,
    users,
    auth_headers,
):
    response = client.post(
        "/api/v1/intelligence/audit-assurance",
        headers=auth_headers(
            users["admin"]
        ),
    )

    assert response.status_code == 405


def test_manager_cannot_see_admin_audit_assurance_data(
    client,
    users,
    auth_headers,
    resource_data,
):
    response = client.get(
        "/api/v1/intelligence/audit-assurance",
        headers=auth_headers(
            users["manager"]
        ),
    )

    assert response.status_code == 200

    body = response.json()

    audit_ids = {
        audit["id"]
        for audit in body["audits"]
    }

    admin_audit = resource_data[
        "audits"
    ]["admin"]

    assert (
        admin_audit.id
        not in audit_ids
    )