from datetime import datetime, timezone


def _payload(
    risk_id,
    owner_id,
    *,
    strategy="Mitigate",
    status="Planned",
):
    return {
        "risk_id": risk_id,
        "strategy": strategy,
        "status": status,
        "treatment_plan": (
            "Implement additional controls and "
            "monitor their effectiveness."
        ),
        "owner_id": owner_id,
        "target_date": None,
        "residual_likelihood": 2,
        "residual_impact": 3,
        "residual_risk_score": 6,
        "acceptance_status": (
            "Pending"
            if strategy == "Accept"
            else "Not Required"
        ),
        "acceptance_reason": (
            "Management review is required before "
            "the residual risk can be accepted."
            if strategy == "Accept"
            else None
        ),
        "accepted_by_id": None,
        "accepted_at": None,
    }


def test_analyst_can_create_treatment_for_own_risk(
    client,
    auth_headers,
    users,
    resource_data,
):
    risk = resource_data["risks"]["analyst"]

    response = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["analyst"]),
        json=_payload(
            risk.id,
            users["analyst"].id,
        ),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["risk_id"] == risk.id
    assert data["owner_id"] == users["analyst"].id
    assert data["strategy"] == "Mitigate"
    assert data["status"] == "Planned"
    assert data["residual_risk_score"] == 6


def test_analyst_cannot_create_treatment_for_hidden_risk(
    client,
    auth_headers,
    users,
    resource_data,
):
    risk = resource_data["risks"]["admin"]

    response = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["analyst"]),
        json=_payload(
            risk.id,
            users["analyst"].id,
        ),
    )

    assert response.status_code == 404


def test_analyst_cannot_assign_treatment_to_other_user(
    client,
    auth_headers,
    users,
    resource_data,
):
    risk = resource_data["risks"]["analyst"]

    response = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["analyst"]),
        json=_payload(
            risk.id,
            users["manager"].id,
        ),
    )

    assert response.status_code == 403


def test_manager_can_create_treatment_for_subordinate(
    client,
    auth_headers,
    users,
    resource_data,
):
    risk = resource_data["risks"]["analyst"]

    response = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["manager"]),
        json=_payload(
            risk.id,
            users["analyst"].id,
        ),
    )

    assert response.status_code == 201


def test_employee_can_create_treatment_for_own_risk(
    client,
    auth_headers,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]

    response = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["employee"]),
        json=_payload(
            risk.id,
            users["employee"].id,
        ),
    )

    assert response.status_code == 201


def test_auditor_can_view_but_cannot_create(
    client,
    auth_headers,
    users,
    resource_data,
):
    risk = resource_data["risks"]["admin"]

    response = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["auditor"]),
        json=_payload(
            risk.id,
            users["admin"].id,
        ),
    )

    assert response.status_code == 403


def test_admin_can_create_treatment_for_any_risk(
    client,
    auth_headers,
    users,
    resource_data,
):
    risk = resource_data["risks"]["admin"]

    response = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["admin"]),
        json=_payload(
            risk.id,
            users["admin"].id,
        ),
    )

    assert response.status_code == 201


def test_list_scope_requires_both_risk_and_treatment_visibility(
    client,
    auth_headers,
    users,
    resource_data,
):
    analyst_risk = resource_data["risks"]["analyst"]
    admin_risk = resource_data["risks"]["admin"]

    response_1 = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["analyst"]),
        json=_payload(
            analyst_risk.id,
            users["analyst"].id,
        ),
    )

    assert response_1.status_code == 201

    response_2 = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["admin"]),
        json=_payload(
            admin_risk.id,
            users["admin"].id,
        ),
    )

    assert response_2.status_code == 201

    response = client.get(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["analyst"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["risk_id"] == analyst_risk.id


def test_risk_treatment_get_for_hidden_risk_returns_404(
    client,
    auth_headers,
    users,
    resource_data,
):
    response = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["admin"]),
        json=_payload(
            resource_data["risks"]["admin"].id,
            users["admin"].id,
        ),
    )

    assert response.status_code == 201

    treatment_id = response.json()["id"]

    hidden_response = client.get(
        f"/api/v1/risk-treatments/{treatment_id}",
        headers=auth_headers(users["analyst"]),
    )

    assert hidden_response.status_code == 404


def test_risk_treatments_for_risk_respect_visibility(
    client,
    auth_headers,
    users,
    resource_data,
):
    own_risk = resource_data["risks"]["analyst"]
    hidden_risk = resource_data["risks"]["admin"]

    own_create = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["analyst"]),
        json=_payload(
            own_risk.id,
            users["analyst"].id,
        ),
    )

    assert own_create.status_code == 201

    hidden_create = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["admin"]),
        json=_payload(
            hidden_risk.id,
            users["admin"].id,
        ),
    )

    assert hidden_create.status_code == 201

    visible = client.get(
        f"/api/v1/risks/{own_risk.id}/treatments",
        headers=auth_headers(users["analyst"]),
    )

    assert visible.status_code == 200
    assert len(visible.json()) == 1

    hidden = client.get(
        f"/api/v1/risks/{hidden_risk.id}/treatments",
        headers=auth_headers(users["analyst"]),
    )

    assert hidden.status_code == 404


def test_employee_cannot_view_admin_treatment(
    client,
    auth_headers,
    users,
    resource_data,
):
    response = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["admin"]),
        json=_payload(
            resource_data["risks"]["admin"].id,
            users["admin"].id,
        ),
    )

    assert response.status_code == 201

    treatment_id = response.json()["id"]

    response = client.get(
        f"/api/v1/risk-treatments/{treatment_id}",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 404


def test_manager_cannot_delete_treatment(
    client,
    auth_headers,
    users,
    resource_data,
):
    response = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["manager"]),
        json=_payload(
            resource_data["risks"]["manager"].id,
            users["manager"].id,
        ),
    )

    assert response.status_code == 201

    treatment_id = response.json()["id"]

    response = client.delete(
        f"/api/v1/risk-treatments/{treatment_id}",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 403


def test_admin_can_delete_treatment(
    client,
    auth_headers,
    users,
    resource_data,
):
    response = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["admin"]),
        json=_payload(
            resource_data["risks"]["admin"].id,
            users["admin"].id,
        ),
    )

    assert response.status_code == 201

    treatment_id = response.json()["id"]

    response = client.delete(
        f"/api/v1/risk-treatments/{treatment_id}",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200

    response = client.get(
        f"/api/v1/risk-treatments/{treatment_id}",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 404


def test_owner_reassignment_must_respect_scope(
    client,
    auth_headers,
    users,
    resource_data,
):
    response = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["analyst"]),
        json=_payload(
            resource_data["risks"]["analyst"].id,
            users["analyst"].id,
        ),
    )

    assert response.status_code == 201

    treatment_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment_id}",
        headers=auth_headers(users["analyst"]),
        json={
            "owner_id": users["manager"].id,
        },
    )

    assert response.status_code == 403


def test_treatment_update_preserves_scope(
    client,
    auth_headers,
    users,
    resource_data,
):
    response = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["analyst"]),
        json=_payload(
            resource_data["risks"]["analyst"].id,
            users["analyst"].id,
        ),
    )

    assert response.status_code == 201

    treatment_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment_id}",
        headers=auth_headers(users["analyst"]),
        json={
            "status": "In Progress",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "In Progress"


def test_acceptance_requires_management_approval(
    client,
    auth_headers,
    users,
    resource_data,
):
    response = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["analyst"]),
        json=_payload(
            resource_data["risks"]["analyst"].id,
            users["analyst"].id,
            strategy="Accept",
        ),
    )

    assert response.status_code == 201

    treatment_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment_id}",
        headers=auth_headers(users["analyst"]),
        json={
            "acceptance_status": "Approved",
        },
    )

    assert response.status_code == 403


def test_manager_can_approve_acceptance(
    client,
    auth_headers,
    users,
    resource_data,
):
    response = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(users["manager"]),
        json=_payload(
            resource_data["risks"]["manager"].id,
            users["manager"].id,
            strategy="Accept",
        ),
    )

    assert response.status_code == 201

    treatment_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment_id}",
        headers=auth_headers(users["manager"]),
        json={
            "acceptance_status": "Approved",
            "acceptance_reason": (
                "Residual risk is within the "
                "approved organisational tolerance."
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["acceptance_status"] == "Approved"
    assert data["accepted_by_id"] == users["manager"].id
    assert data["accepted_at"] is not None


def test_unauthenticated_risk_treatment_list_is_rejected(
    client,
):
    response = client.get(
        "/api/v1/risk-treatments/"
    )

    assert response.status_code == 401