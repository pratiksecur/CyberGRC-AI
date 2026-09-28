from unittest.mock import patch

from app.models.risk import Risk


def _risk(db, users, *, score=20, owner="analyst"):
    risk = Risk(
        title="Phase 56 AI Hardening Risk",
        description="Risk used for Phase 56 AI hardening tests.",
        likelihood=4,
        impact=5,
        risk_score=score,
        status="Open",
        owner_id=users[owner].id,
        created_by_id=users[owner].id,
    )

    db.add(risk)
    db.commit()
    db.refresh(risk)

    return risk


def _valid_response():
    return """
    {
        "explanation": "The deterministic risk state indicates that the current GRC conditions require human review of the existing treatment assessment.",
        "key_drivers": [
            "The current deterministic risk state requires review."
        ],
        "review_areas": [
            "Review the current treatment assessment."
        ]
    }
    """


# ==========================================================
# INVALID JSON -> RETRY -> SUCCESS
# ==========================================================


def test_phase56_ai_invalid_json_retries(
    client,
    db,
    users,
    auth_headers,
):
    risk = _risk(db, users)

    with patch(
        "app.services.ai.continuous_risk_state_ai_service.get_ai_provider"
    ) as mock_provider:

        mock_provider.return_value.generate.side_effect = [
            "this is not json",
            _valid_response(),
        ]

        response = client.post(
            f"/api/v1/ai/risk/{risk.id}/state-explanation",
            headers=auth_headers(users["manager"]),
        )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_state"] == "REASSESSMENT_REQUIRED"

    assert (
        mock_provider.return_value.generate.call_count
        == 2
    )


# ==========================================================
# INVALID JSON TWICE -> FAIL CLOSED
# ==========================================================


def test_phase56_ai_invalid_json_twice_fails_closed(
    client,
    db,
    users,
    auth_headers,
):
    risk = _risk(db, users)

    with patch(
        "app.services.ai.continuous_risk_state_ai_service.get_ai_provider"
    ) as mock_provider:

        mock_provider.return_value.generate.side_effect = [
            "invalid response",
            "still invalid",
        ]

        response = client.post(
            f"/api/v1/ai/risk/{risk.id}/state-explanation",
            headers=auth_headers(users["manager"]),
        )

    assert response.status_code == 502

    assert (
        mock_provider.return_value.generate.call_count
        == 2
    )


# ==========================================================
# INVALID SCHEMA -> RETRY -> SUCCESS
# ==========================================================


def test_phase56_ai_invalid_schema_retries(
    client,
    db,
    users,
    auth_headers,
):
    risk = _risk(db, users)

    invalid_schema = """
    {
        "explanation": "too short"
    }
    """

    with patch(
        "app.services.ai.continuous_risk_state_ai_service.get_ai_provider"
    ) as mock_provider:

        mock_provider.return_value.generate.side_effect = [
            invalid_schema,
            _valid_response(),
        ]

        response = client.post(
            f"/api/v1/ai/risk/{risk.id}/state-explanation",
            headers=auth_headers(users["manager"]),
        )

    assert response.status_code == 200

    assert (
        mock_provider.return_value.generate.call_count
        == 2
    )


# ==========================================================
# PROVIDER FAILURE
# ==========================================================


def test_phase56_ai_provider_failure_returns_503(
    client,
    db,
    users,
    auth_headers,
):
    risk = _risk(db, users)

    with patch(
        "app.services.ai.continuous_risk_state_ai_service.get_ai_provider"
    ) as mock_provider:

        mock_provider.return_value.generate.side_effect = (
            RuntimeError("provider unavailable")
        )

        response = client.post(
            f"/api/v1/ai/risk/{risk.id}/state-explanation",
            headers=auth_headers(users["manager"]),
        )

    assert response.status_code == 503


# ==========================================================
# AI OUTPUT CANNOT CHANGE AUTHORITATIVE STATE
# ==========================================================


def test_phase56_ai_output_never_controls_state(
    client,
    db,
    users,
    auth_headers,
):
    risk = _risk(
        db,
        users,
        score=20,
        owner="analyst",
    )

    misleading_response = """
    {
        "explanation": "Everything is safe and no reassessment is necessary.",
        "key_drivers": [
            "The risk appears safe."
        ],
        "review_areas": [
            "No review is necessary."
        ]
    }
    """

    with patch(
        "app.services.ai.continuous_risk_state_ai_service.get_ai_provider"
    ) as mock_provider:

        mock_provider.return_value.generate.return_value = (
            misleading_response
        )

        response = client.post(
            f"/api/v1/ai/risk/{risk.id}/state-explanation",
            headers=auth_headers(users["manager"]),
        )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_state"] == "REASSESSMENT_REQUIRED"
    assert data["reassessment_required"] is True