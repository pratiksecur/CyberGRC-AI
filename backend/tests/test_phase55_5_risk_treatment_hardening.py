from datetime import datetime, timezone


def _payload(risk_id, owner_id, *, strategy="Mitigate", status="Planned"):
    return {
        "risk_id": risk_id,
        "strategy": strategy,
        "status": status,
        "treatment_plan": "Implement additional controls and continuously review effectiveness.",
        "owner_id": owner_id,
        "target_date": None,
        "residual_likelihood": 2,
        "residual_impact": 3,
        "residual_risk_score": 6,
        "acceptance_status": "Pending" if strategy == "Accept" else "Not Required",
        "acceptance_reason": (
            "Management review is required before residual risk can be accepted."
            if strategy == "Accept" else None
        ),
        "accepted_by_id": None,
        "accepted_at": None,
    }


def _create(client, auth_headers, user, risk, *, strategy="Mitigate", status="Planned"):
    response = client.post(
        "/api/v1/risk-treatments/",
        headers=auth_headers(user),
        json=_payload(risk.id, user.id, strategy=strategy, status=status),
    )
    assert response.status_code == 201
    return response.json()


def test_phase55_5_planned_can_move_to_in_progress(
    client, auth_headers, users, resource_data
):
    treatment = _create(
        client, auth_headers, users["analyst"], resource_data["risks"]["analyst"]
    )

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment['id']}",
        headers=auth_headers(users["analyst"]),
        json={"status": "In Progress"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "In Progress"


def test_phase55_5_planned_cannot_jump_directly_to_completed(
    client, auth_headers, users, resource_data
):
    treatment = _create(
        client, auth_headers, users["analyst"], resource_data["risks"]["analyst"]
    )

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment['id']}",
        headers=auth_headers(users["analyst"]),
        json={"status": "Completed"},
    )

    assert response.status_code == 400
    assert "status transition" in response.json()["detail"].lower()


def test_phase55_5_in_progress_can_complete(
    client, auth_headers, users, resource_data
):
    treatment = _create(
        client, auth_headers, users["analyst"], resource_data["risks"]["analyst"]
    )

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment['id']}",
        headers=auth_headers(users["analyst"]),
        json={"status": "In Progress"},
    )
    assert response.status_code == 200

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment['id']}",
        headers=auth_headers(users["analyst"]),
        json={"status": "Completed"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Completed"


def test_phase55_5_completed_is_terminal(
    client, auth_headers, users, resource_data
):
    treatment = _create(
        client, auth_headers, users["analyst"], resource_data["risks"]["analyst"]
    )

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment['id']}",
        headers=auth_headers(users["analyst"]),
        json={"status": "In Progress"},
    )
    assert response.status_code == 200

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment['id']}",
        headers=auth_headers(users["analyst"]),
        json={"status": "Completed"},
    )
    assert response.status_code == 200

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment['id']}",
        headers=auth_headers(users["analyst"]),
        json={"status": "In Progress"},
    )

    assert response.status_code == 400


def test_phase55_5_cancelled_is_terminal(
    client, auth_headers, users, resource_data
):
    treatment = _create(
        client, auth_headers, users["analyst"], resource_data["risks"]["analyst"]
    )

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment['id']}",
        headers=auth_headers(users["analyst"]),
        json={"status": "Cancelled"},
    )
    assert response.status_code == 200

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment['id']}",
        headers=auth_headers(users["analyst"]),
        json={"status": "In Progress"},
    )

    assert response.status_code == 400


def test_phase55_5_final_acceptance_requires_reason(
    client, auth_headers, users, resource_data
):
    treatment = _create(
        client,
        auth_headers,
        users["analyst"],
        resource_data["risks"]["analyst"],
        strategy="Accept",
    )

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment['id']}",
        headers=auth_headers(users["manager"]),
        json={"acceptance_status": "Approved"},
    )

    assert response.status_code == 400
    assert "acceptance_reason" in response.json()["detail"]


def test_phase55_5_final_acceptance_metadata_cannot_be_replaced(
    client, auth_headers, users, resource_data
):
    treatment = _create(
        client,
        auth_headers,
        users["analyst"],
        resource_data["risks"]["analyst"],
        strategy="Accept",
    )

    reason = "Residual risk is within the approved organisational tolerance."
    response = client.patch(
        f"/api/v1/risk-treatments/{treatment['id']}",
        headers=auth_headers(users["manager"]),
        json={
            "acceptance_status": "Approved",
            "acceptance_reason": reason,
        },
    )
    assert response.status_code == 200
    approved = response.json()
    assert approved["accepted_by_id"] == users["manager"].id
    assert approved["accepted_at"] is not None

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment['id']}",
        headers=auth_headers(users["admin"]),
        json={
            "acceptance_status": "Rejected",
            "acceptance_reason": "Attempted replacement of final decision.",
        },
    )

    assert response.status_code == 403

    response = client.get(
        f"/api/v1/risk-treatments/{treatment['id']}",
        headers=auth_headers(users["admin"]),
    )
    assert response.status_code == 200
    final_data = response.json()
    assert final_data["acceptance_status"] == "Approved"
    assert final_data["accepted_by_id"] == users["manager"].id
    assert final_data["acceptance_reason"] == reason


def test_phase55_5_client_cannot_supply_approval_identity(
    client, auth_headers, users, resource_data
):
    treatment = _create(
        client,
        auth_headers,
        users["analyst"],
        resource_data["risks"]["analyst"],
        strategy="Accept",
    )

    response = client.patch(
        f"/api/v1/risk-treatments/{treatment['id']}",
        headers=auth_headers(users["manager"]),
        json={
            "acceptance_status": "Approved",
            "acceptance_reason": "Approved after management review.",
            "accepted_by_id": users["admin"].id,
            "accepted_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["accepted_by_id"] == users["manager"].id
    assert data["accepted_by_id"] != users["admin"].id
