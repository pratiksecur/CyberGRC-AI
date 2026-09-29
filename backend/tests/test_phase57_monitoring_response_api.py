from app.models.risk import Risk


# ==========================================================
# HELPERS
# ==========================================================

def _risk(
    db,
    users,
    *,
    score=12,
    owner="analyst",
):
    risk = Risk(
        title="Phase 57 Monitoring API Risk",
        description="Risk used for Phase 57 monitoring API testing.",
        likelihood=3,
        impact=4,
        risk_score=score,
        status="Open",
        owner_id=users[owner].id,
        created_by_id=users[owner].id,
    )

    db.add(risk)
    db.commit()
    db.refresh(risk)

    return risk


# ==========================================================
# OVERVIEW RESPONSE
# ==========================================================

def test_phase57_monitoring_overview_api_exposes_response_metrics(
    client,
    db,
    users,
    auth_headers,
):
    risk = _risk(
        db,
        users,
        score=12,
    )

    response = client.get(
        "/api/v1/monitoring/overview",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert "metrics" in data

    metrics = data["metrics"]

    assert (
        "response_required_risks"
        in metrics
    )

    assert (
        "human_approval_required_risks"
        in metrics
    )

    assert (
        "critical_response_risks"
        in metrics
    )

    assert isinstance(
        metrics["response_required_risks"],
        int,
    )

    assert isinstance(
        metrics["human_approval_required_risks"],
        int,
    )

    assert isinstance(
        metrics["critical_response_risks"],
        int,
    )

    assert "risk_responses" in data

    assert isinstance(
        data["risk_responses"],
        list,
    )

    returned = next(
        item
        for item in data["risk_responses"]
        if item["risk_id"] == risk.id
    )

    assert "risk_state" in returned

    assert "treatment_state" in returned

    assert "reassessment_required" in returned

    assert "response_required" in returned

    assert "priority" in returned

    assert "human_approval_required" in returned

    assert "decisions" in returned

    assert isinstance(
        returned["decisions"],
        list,
    )


# ==========================================================
# VALID RESPONSE VALUES
# ==========================================================

def test_phase57_monitoring_overview_api_exposes_valid_response_values(
    client,
    db,
    users,
    auth_headers,
):
    risk = _risk(
        db,
        users,
        score=12,
    )

    response = client.get(
        "/api/v1/monitoring/overview",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    data = response.json()

    risk_response = next(
        item
        for item in data["risk_responses"]
        if item["risk_id"] == risk.id
    )

    assert risk_response["risk_state"] in {
        "CURRENT",
        "DEGRADED",
        "REASSESSMENT_REQUIRED",
    }

    assert risk_response["treatment_state"] in {
        "CURRENT",
        "STALE",
        "DEGRADED",
        "REQUIRES_REASSESSMENT",
    }

    assert risk_response["priority"] in {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }

    for decision in risk_response["decisions"]:
        assert decision["decision"] in {
            "MONITOR",
            "REVIEW",
            "REASSESS_RISK",
            "UPDATE_TREATMENT",
            "CORRECTIVE_ACTION_REVIEW",
            "CONTROL_REVIEW",
            "EVIDENCE_REVIEW",
            "ESCALATE",
        }

        assert decision["priority"] in {
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL",
        }

        assert isinstance(
            decision["reason_codes"],
            list,
        )

        assert isinstance(
            decision["human_approval_required"],
            bool,
        )


# ==========================================================
# AUTHENTICATION
# ==========================================================

def test_phase57_monitoring_overview_api_requires_authentication(
    client,
):
    response = client.get(
        "/api/v1/monitoring/overview",
    )

    assert response.status_code == 401


# ==========================================================
# OBJECT-LEVEL VISIBILITY
# ==========================================================

def test_phase57_monitoring_overview_api_hides_out_of_scope_risk(
    client,
    db,
    users,
    auth_headers,
):
    risk = _risk(
        db,
        users,
        score=12,
        owner="admin",
    )

    response = client.get(
        "/api/v1/monitoring/overview",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    data = response.json()

    returned_ids = {
        item["risk_id"]
        for item in data["risk_responses"]
    }

    assert risk.id not in returned_ids


# ==========================================================
# RESPONSE DECISION STRUCTURE
# ==========================================================

def test_phase57_monitoring_api_decisions_are_structured(
    client,
    db,
    users,
    auth_headers,
):
    risk = _risk(
        db,
        users,
        score=12,
    )

    response = client.get(
        "/api/v1/monitoring/overview",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    data = response.json()

    risk_response = next(
        item
        for item in data["risk_responses"]
        if item["risk_id"] == risk.id
    )

    for decision in risk_response["decisions"]:
        assert "decision" in decision
        assert "priority" in decision
        assert "reason_codes" in decision
        assert "human_approval_required" in decision