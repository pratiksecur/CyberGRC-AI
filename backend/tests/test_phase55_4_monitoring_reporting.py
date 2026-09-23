from datetime import datetime, timedelta, timezone

from app.models.risk import Risk
from app.models.risk_treatment import RiskTreatment
from app.services.grc_monitoring_service import get_monitoring_overview, get_risk_monitoring
from app.services.reports_service import get_risk_report


def _add_treatment(db, *, risk_id, owner_id, strategy="Mitigate", status="Planned",
                   target_date=None, residual_likelihood=None, residual_impact=None,
                   residual_risk_score=None, acceptance_status="Not Required",
                   updated_at=None):
    treatment = RiskTreatment(
        risk_id=risk_id, strategy=strategy, status=status,
        treatment_plan="Implement and continuously review the treatment controls.",
        owner_id=owner_id, target_date=target_date,
        residual_likelihood=residual_likelihood,
        residual_impact=residual_impact,
        residual_risk_score=residual_risk_score,
        acceptance_status=acceptance_status,
        accepted_by_id=(2 if acceptance_status == "Approved" else None),
        accepted_at=(datetime.now(timezone.utc) if acceptance_status == "Approved" else None),
        updated_at=updated_at,
    )
    db.add(treatment); db.commit(); db.refresh(treatment)
    return treatment


def _risk(db, users, *, score=20, owner="analyst"):
    user = users[owner]
    risk = Risk(
        title="Phase 55.4 Treatment Risk",
        description="Risk used for Phase 55.4 treatment intelligence tests.",
        likelihood=4, impact=5, risk_score=score, status="Open",
        owner_id=user.id, created_by_id=user.id,
    )
    db.add(risk); db.commit(); db.refresh(risk)
    return risk


def _alert_types(response):
    return [alert.alert_type for alert in response.alerts]


def test_phase55_4_monitoring_overdue_treatment(db, users):
    risk = _risk(db, users)
    _add_treatment(db, risk_id=risk.id, owner_id=users["analyst"].id,
                   status="In Progress",
                   target_date=datetime.now(timezone.utc).date() - timedelta(days=1),
                   residual_likelihood=3, residual_impact=3, residual_risk_score=9)
    response = get_risk_monitoring(db, risk.id, users["manager"])
    assert response is not None
    assert "OVERDUE_RISK_TREATMENT" in _alert_types(response)


def test_phase55_4_monitoring_stuck_treatment(db, users):
    risk = _risk(db, users, score=12)
    treatment = _add_treatment(db, risk_id=risk.id, owner_id=users["analyst"].id,
                               status="In Progress", residual_likelihood=2,
                               residual_impact=2, residual_risk_score=4)
    treatment.updated_at = datetime.now(timezone.utc) - timedelta(days=31)
    db.commit()
    response = get_risk_monitoring(db, risk.id, users["manager"])
    assert response is not None
    assert "STUCK_RISK_TREATMENT" in _alert_types(response)


def test_phase55_4_monitoring_planned_high_risk(db, users):
    risk = _risk(db, users, score=16)
    _add_treatment(db, risk_id=risk.id, owner_id=users["analyst"].id, status="Planned")
    response = get_risk_monitoring(db, risk.id, users["manager"])
    assert response is not None
    assert "PLANNED_HIGH_RISK_TREATMENT" in _alert_types(response)


def test_phase55_4_monitoring_pending_and_approved_acceptance(db, users):
    risk = _risk(db, users)
    _add_treatment(db, risk_id=risk.id, owner_id=users["analyst"].id,
                   strategy="Accept", status="Planned", residual_likelihood=3,
                   residual_impact=3, residual_risk_score=9, acceptance_status="Pending")
    approved = _add_treatment(db, risk_id=risk.id, owner_id=users["analyst"].id,
                              strategy="Accept", status="Completed", residual_likelihood=2,
                              residual_impact=2, residual_risk_score=4, acceptance_status="Approved")
    response = get_risk_monitoring(db, risk.id, users["manager"])
    assert response is not None
    types = _alert_types(response)
    assert "PENDING_RISK_ACCEPTANCE" in types
    assert "APPROVED_RISK_ACCEPTANCE" in types
    assert approved.id in [a.resource_id for a in response.alerts if a.alert_type == "APPROVED_RISK_ACCEPTANCE"]


def test_phase55_4_monitoring_cancelled_without_replacement(db, users):
    risk = _risk(db, users)
    _add_treatment(db, risk_id=risk.id, owner_id=users["analyst"].id, status="Cancelled")
    response = get_risk_monitoring(db, risk.id, users["manager"])
    assert response is not None
    assert "CANCELLED_TREATMENT_WITHOUT_REPLACEMENT" in _alert_types(response)


def test_phase55_4_monitoring_elevated_residual_risk(db, users):
    risk = _risk(db, users)
    treatment = _add_treatment(db, risk_id=risk.id, owner_id=users["analyst"].id,
                               status="Completed", residual_likelihood=4,
                               residual_impact=4, residual_risk_score=16)
    response = get_risk_monitoring(db, risk.id, users["manager"])
    assert response is not None
    alerts = [a for a in response.alerts if a.alert_type == "ELEVATED_TREATMENT_RESIDUAL_RISK"]
    assert len(alerts) == 1
    assert alerts[0].resource_id == treatment.id
    assert alerts[0].severity == "HIGH"


def test_phase55_4_monitoring_treatment_visibility_boundary(db, users):
    risk = _risk(db, users)
    _add_treatment(db, risk_id=risk.id, owner_id=users["admin"].id, status="Planned")
    response = get_risk_monitoring(db, risk.id, users["manager"])
    assert response is not None
    assert not any(a.resource_type == "risk_treatment" for a in response.alerts)


def test_phase55_4_monitoring_metrics_include_treatments(db, users):
    risk = _risk(db, users)
    _add_treatment(db, risk_id=risk.id, owner_id=users["analyst"].id, status="Planned")
    response = get_monitoring_overview(db, users["manager"])
    assert response.metrics.treatment_alerts >= 1
    assert response.metrics.planned_high_risk_treatments >= 1


def test_phase55_4_risk_report_exposes_treatment_aware_residual(db, users):
    risk = _risk(db, users, score=20)
    treatment = _add_treatment(db, risk_id=risk.id, owner_id=users["analyst"].id,
                               status="Completed", residual_likelihood=2,
                               residual_impact=3, residual_risk_score=6)
    report = get_risk_report(db, [users["manager"].id, users["analyst"].id])
    item = next(item for item in report["risks"] if item["id"] == risk.id)
    assert item["treatment_count"] == 1
    assert item["effective_treatment_count"] == 1
    assert item["selected_treatment_id"] == treatment.id
    assert item["treatment_residual_risk"] == 6
    assert item["treatment_aware_residual_risk"] == 6.0
    assert report["summary"]["risks_with_effective_treatment"] >= 1


def test_phase55_4_risk_report_falls_back_to_control_estimate_without_treatment(db, users):
    risk = _risk(db, users, score=20)
    report = get_risk_report(db, [users["manager"].id, users["analyst"].id])
    item = next(item for item in report["risks"] if item["id"] == risk.id)
    assert item["treatment_count"] == 0
    assert item["treatment_residual_risk"] is None
    assert item["treatment_aware_residual_risk"] == 20.0
    assert item["control_estimated_residual_risk"] == 20.0
