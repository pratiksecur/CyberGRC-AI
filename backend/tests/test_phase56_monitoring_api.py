from datetime import date

from app.models.audit import Audit
from app.models.framework import Framework
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
        title="Phase 56 API Risk",
        description="Risk used for Phase 56 API testing.",
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


def _audit(db, users):
    framework = Framework(
        name="Phase 56 API Framework",
        version="1.0",
        description="Framework used for Phase 56 API testing.",
    )

    db.add(framework)
    db.commit()
    db.refresh(framework)

    audit = Audit(
        name="Phase 56 API Audit",
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


# ==========================================================
# RISK MONITORING API
# ==========================================================

def test_phase56_risk_monitoring_api_exposes_state(
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

    response = client.get(
        f"/api/v1/monitoring/risk/{risk.id}",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_id"] == risk.id

    assert "continuous_risk_state" in data
    assert "treatment_state" in data
    assert "reassessment_required" in data
    assert "state_reasons" in data

    assert isinstance(
        data["continuous_risk_state"],
        str,
    )

    assert isinstance(
        data["treatment_state"],
        str,
    )

    assert isinstance(
        data["reassessment_required"],
        bool,
    )

    assert isinstance(
        data["state_reasons"],
        list,
    )


def test_phase56_risk_monitoring_api_exposes_valid_state_values(
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

    response = client.get(
        f"/api/v1/monitoring/risk/{risk.id}",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["continuous_risk_state"] in {
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


# ==========================================================
# MONITORING OVERVIEW API
# ==========================================================

def test_phase56_monitoring_overview_api_exposes_state_metrics(
    client,
    db,
    users,
    auth_headers,
):
    _risk(
        db,
        users,
        score=20,
        owner="analyst",
    )

    response = client.get(
        "/api/v1/monitoring/overview",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert "metrics" in data

    metrics = data["metrics"]

    assert "degraded_risks" in metrics
    assert "reassessment_required_risks" in metrics

    assert isinstance(
        metrics["degraded_risks"],
        int,
    )

    assert isinstance(
        metrics["reassessment_required_risks"],
        int,
    )


# ==========================================================
# AUTHENTICATION
# ==========================================================

def test_phase56_monitoring_api_requires_authentication(
    client,
    db,
    users,
):
    risk = _risk(
        db,
        users,
        owner="analyst",
    )

    response = client.get(
        f"/api/v1/monitoring/risk/{risk.id}",
    )

    assert response.status_code == 401


# ==========================================================
# OBJECT-LEVEL VISIBILITY / BOLA
# ==========================================================

def test_phase56_monitoring_api_hides_out_of_scope_risk(
    client,
    db,
    users,
    auth_headers,
):
    """
    GRC Manager must not be able to retrieve monitoring
    information for an Admin-owned Risk.

    The API intentionally returns 404 so that the existence
    of the protected Risk is not disclosed.
    """

    risk = _risk(
        db,
        users,
        owner="admin",
    )

    response = client.get(
        f"/api/v1/monitoring/risk/{risk.id}",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 404


# ==========================================================
# STATE REASON STRUCTURE
# ==========================================================

def test_phase56_monitoring_api_state_reasons_are_structured(
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

    response = client.get(
        f"/api/v1/monitoring/risk/{risk.id}",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    data = response.json()

    for reason in data["state_reasons"]:
        assert "code" in reason
        assert "severity" in reason
        assert "message" in reason
        assert "resource_type" in reason
        assert "resource_id" in reason