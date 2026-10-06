def test_admin_can_access_executive_intelligence(
    client,
    users,
    auth_headers,
):
    response = client.get(
        "/api/v1/intelligence/executive",
        headers=auth_headers(
            users["admin"]
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert "risk_posture" in body
    assert "compliance_posture" in body
    assert "control_health" in body
    assert "explainability" in body


def test_manager_can_access_executive_intelligence(
    client,
    users,
    auth_headers,
):
    response = client.get(
        "/api/v1/intelligence/executive",
        headers=auth_headers(
            users["manager"]
        ),
    )

    assert response.status_code == 200


def test_unauthenticated_cannot_access_executive_intelligence(
    client,
):
    response = client.get(
        "/api/v1/intelligence/executive"
    )

    assert response.status_code == 401


def test_employee_visibility_is_scoped(
    client,
    users,
    auth_headers,
):
    response = client.get(
        "/api/v1/intelligence/executive",
        headers=auth_headers(
            users["employee"]
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["scope"][
        "visible_user_count"
    ] >= 1