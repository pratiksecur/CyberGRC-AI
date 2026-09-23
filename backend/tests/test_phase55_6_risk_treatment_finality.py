def _payload(risk_id, owner_id):
    return {
        "risk_id": risk_id,
        "strategy": "Accept",
        "status": "Planned",
        "treatment_plan": (
            "Document the risk acceptance rationale and "
            "maintain ongoing monitoring."
        ),
        "owner_id": owner_id,
        "target_date": None,
        "residual_likelihood": 2,
        "residual_impact": 3,
        "residual_risk_score": 6,
        "acceptance_status": "Pending",
        "acceptance_reason": "Management review is required before final acceptance.",
        "accepted_by_id": None,
        "accepted_at": None,
    }


def _create_pending(client, auth_headers, user, risk):
    response = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(user),
        json=_payload(risk.id, user.id),
    )
    assert response.status_code == 201
    return response.json()


def _finalize(client, auth_headers, manager, treatment_id, status):
    response = client.patch(
        f"/api/v1/risk-treatments/{treatment_id}",
        headers=auth_headers(manager),
        json={
            "acceptance_status": status,
            "acceptance_reason": f"Final {status.lower()} decision documented by management.",
        },
    )
    assert response.status_code == 200
    return response.json()


def test_phase55_6_approved_accept_cannot_change_strategy(
    client, auth_headers, users, resource_data
):
    treatment = _create_pending(
        client,
        auth_headers,
        users["analyst"],
        resource_data["risks"]["analyst"],
    )

    _finalize(
        client,
        auth_headers,
        users["manager"],
        treatment["id"],
        "Approved",
    )

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment['id']}",
        headers=auth_headers(users["manager"]),
        json={"strategy": "Mitigate"},
    )

    assert response.status_code == 403
    assert "cannot change treatment strategy" in response.json()["detail"]


def test_phase55_6_rejected_accept_cannot_change_strategy(
    client, auth_headers, users, resource_data
):
    treatment = _create_pending(
        client,
        auth_headers,
        users["analyst"],
        resource_data["risks"]["analyst"],
    )

    _finalize(
        client,
        auth_headers,
        users["manager"],
        treatment["id"],
        "Rejected",
    )

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment['id']}",
        headers=auth_headers(users["manager"]),
        json={"strategy": "Avoid"},
    )

    assert response.status_code == 403
    assert "cannot change treatment strategy" in response.json()["detail"]


def test_phase55_6_pending_accept_can_change_strategy(
    client, auth_headers, users, resource_data
):
    treatment = _create_pending(
        client,
        auth_headers,
        users["analyst"],
        resource_data["risks"]["analyst"],
    )

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment['id']}",
        headers=auth_headers(users["analyst"]),
        json={"strategy": "Mitigate"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["strategy"] == "Mitigate"
    assert data["acceptance_status"] == "Not Required"
    assert data["acceptance_reason"] is None
    assert data["accepted_by_id"] is None
    assert data["accepted_at"] is None


def test_phase55_6_final_acceptance_can_update_non_acceptance_fields(
    client, auth_headers, users, resource_data
):
    treatment = _create_pending(
        client,
        auth_headers,
        users["analyst"],
        resource_data["risks"]["analyst"],
    )

    _finalize(
        client,
        auth_headers,
        users["manager"],
        treatment["id"],
        "Approved",
    )

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment['id']}",
        headers=auth_headers(users["manager"]),
        json={
            "treatment_plan": (
                "Updated operational treatment plan with continued monitoring."
            )
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["strategy"] == "Accept"
    assert data["acceptance_status"] == "Approved"
    assert data["treatment_plan"].startswith("Updated operational")
    assert data["accepted_by_id"] == users["manager"].id
    assert data["accepted_at"] is not None
