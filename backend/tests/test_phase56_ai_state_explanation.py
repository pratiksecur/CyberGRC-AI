from datetime import date
from unittest.mock import patch

from app.models.audit import Audit
from app.models.framework import Framework
from app.models.risk import Risk


def _risk(db, users, *, score=20, owner="analyst"):
    risk = Risk(
        title="Phase 56 AI Risk",
        description="Risk used for Phase 56 AI state explanation testing.",
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


def _audit(db, users):
    framework = Framework(
        name="Phase 56 AI Framework",
        version="1.0",
        description="Framework used for Phase 56 AI testing.",
    )

    db.add(framework)
    db.commit()
    db.refresh(framework)

    audit = Audit(
        name="Phase 56 AI Audit",
        framework_id=framework.id,
        auditor_id=users["auditor"].id,
        created_by_id=users["analyst"].id,
        scope="Organization",
        status="Completed",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )

    db.add(audit)
    db.commit()
    db.refresh(audit)

    return audit


def _mock_ai_response():
    return """
    {
        "explanation": "The risk requires reassessment because the current GRC conditions indicate that the existing treatment assessment should be reviewed by an authorized human decision maker.",
        "key_drivers": [
            "The deterministic risk state requires reassessment.",
            "The current treatment assessment requires review."
        ],
        "review_areas": [
            "Review the current risk treatment.",
            "Review the supporting GRC conditions."
        ]
    }
    """


# ==========================================================
# BASIC AI STATE EXPLANATION
# ==========================================================


def test_phase56_ai_state_explanation_returns_deterministic_state(
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

    with patch(
        "app.services.ai.continuous_risk_state_ai_service.get_ai_provider"
    ) as mock_provider:

        mock_provider.return_value.generate.return_value = (
            _mock_ai_response()
        )

        response = client.post(
            f"/api/v1/ai/risk/{risk.id}/state-explanation",
            headers=auth_headers(users["manager"]),
        )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_state"] in {
        "CURRENT",
        "DEGRADED",
        "REASSESSMENT_REQUIRED",
    }

    assert data["treatment_state"] in {
        "CURRENT",
        "STALE",
        "DEGRADED",
        "REQUIRES_REASSESSMENT",
    }

    assert isinstance(
        data["reassessment_required"],
        bool,
    )

    assert isinstance(
        data["explanation"],
        str,
    )

    assert len(data["explanation"]) >= 30

    assert isinstance(
        data["key_drivers"],
        list,
    )

    assert isinstance(
        data["review_areas"],
        list,
    )


# ==========================================================
# AI CANNOT OVERRIDE DETERMINISTIC STATE
# ==========================================================


def test_phase56_ai_cannot_override_deterministic_state(
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

    malicious_ai_response = """
    {
        "explanation": "The risk is completely safe and no review is necessary.",
        "key_drivers": [
            "The risk is safe."
        ],
        "review_areas": [
            "No review is required."
        ]
    }
    """

    with patch(
        "app.services.ai.continuous_risk_state_ai_service.get_ai_provider"
    ) as mock_provider:

        mock_provider.return_value.generate.return_value = (
            malicious_ai_response
        )

        response = client.post(
            f"/api/v1/ai/risk/{risk.id}/state-explanation",
            headers=auth_headers(users["manager"]),
        )

    assert response.status_code == 200

    data = response.json()

    # The state is supplied by the deterministic engine,
    # not by the AI response.
    assert data["risk_state"] == "REASSESSMENT_REQUIRED"
    assert data["reassessment_required"] is True


# ==========================================================
# OUT-OF-SCOPE RISK
# ==========================================================


def test_phase56_ai_state_explanation_hides_out_of_scope_risk(
    client,
    db,
    users,
    auth_headers,
):
    risk = _risk(
        db,
        users,
        score=20,
        owner="admin",
    )

    with patch(
        "app.services.ai.continuous_risk_state_ai_service.get_ai_provider"
    ) as mock_provider:

        response = client.post(
            f"/api/v1/ai/risk/{risk.id}/state-explanation",
            headers=auth_headers(users["manager"]),
        )

    assert response.status_code == 404

    mock_provider.assert_not_called()


# ==========================================================
# AI PERMISSION
# ==========================================================


def test_phase56_ai_state_explanation_requires_ai_permission(
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

    response = client.post(
        f"/api/v1/ai/risk/{risk.id}/state-explanation",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 403


# ==========================================================
# AUTHENTICATION
# ==========================================================


def test_phase56_ai_state_explanation_requires_authentication(
    client,
    db,
    users,
):
    risk = _risk(
        db,
        users,
        score=20,
        owner="analyst",
    )

    response = client.post(
        f"/api/v1/ai/risk/{risk.id}/state-explanation"
    )

    assert response.status_code == 401