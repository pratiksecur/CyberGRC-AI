from datetime import date

from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.control import Control
from app.models.risk import Risk
from app.models.risk_control import RiskControl
from app.models.risk_treatment import RiskTreatment
from app.models.framework import Framework

from app.services.continuous_risk_state_service import (
    get_continuous_risk_state,
)
from app.services.grc_monitoring_service import (
    get_monitoring_overview,
    get_risk_monitoring,
)


def _risk(
    db,
    users,
    *,
    score=12,
):
    user = users["analyst"]

    risk = Risk(
        title="Phase 56 Monitoring Risk",
        description="Risk used for Phase 56 monitoring testing.",
        likelihood=3,
        impact=4,
        risk_score=score,
        status="Open",
        owner_id=user.id,
        created_by_id=user.id,
    )

    db.add(risk)
    db.commit()
    db.refresh(risk)

    return risk


def _treatment(
    db,
    users,
    risk,
    *,
    status="Completed",
    residual_likelihood=2,
    residual_impact=3,
    target_date=None,
):
    treatment = RiskTreatment(
        risk_id=risk.id,
        strategy="Mitigate",
        status=status,
        treatment_plan="Maintain treatment.",
        owner_id=users["analyst"].id,
        target_date=(
            target_date
            if target_date is not None
            else date(2026, 12, 31)
        ),
        residual_likelihood=residual_likelihood,
        residual_impact=residual_impact,
        residual_risk_score=(
            residual_likelihood * residual_impact
            if (
                residual_likelihood is not None
                and residual_impact is not None
            )
            else None
        ),
        acceptance_status="Not Required",
    )

    db.add(treatment)
    db.commit()
    db.refresh(treatment)

    return treatment


def _control(
    db,
    users,
    *,
    effectiveness=80,
    status="Active",
):
    control = Control(
        title="Phase 56 Monitoring Control",
        description="Control used for monitoring testing.",
        control_type="Preventive",
        status=status,
        effectiveness=effectiveness,
        owner_id=users["analyst"].id,
        created_by_id=users["analyst"].id,
    )

    db.add(control)
    db.commit()
    db.refresh(control)

    return control


def _connect_control(
    db,
    risk,
    control,
):
    mapping = RiskControl(
        risk_id=risk.id,
        control_id=control.id,
    )

    db.add(mapping)
    db.commit()
    db.refresh(mapping)

    return mapping


def _audit(
    db,
    users,
):
    framework = Framework(
        name="Phase 56 Monitoring Framework",
        version="1.0",
        description="Framework used for Phase 56 monitoring tests.",
    )

    db.add(framework)
    db.commit()
    db.refresh(framework)

    audit = Audit(
        name="Phase 56 Monitoring Audit",
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


def _finding(
    db,
    audit,
    control,
    *,
    severity="High",
    status="Open",
):
    finding = AuditFinding(
        audit_id=audit.id,
        control_id=control.id,
        title="Phase 56 Monitoring Finding",
        description="Finding used for monitoring testing.",
        severity=severity,
        recommendation="Remediate the issue.",
        status=status,
    )

    db.add(finding)
    db.commit()
    db.refresh(finding)

    return finding


def _alert_types(response):
    return [
        alert.alert_type
        for alert in response.alerts
    ]


def test_phase56_monitoring_current_risk_has_no_state_alert(
    db,
    users,
):
    risk = _risk(
        db,
        users,
        score=12,
    )

    _treatment(
        db,
        users,
        risk,
    )

    response = get_risk_monitoring(
        db,
        risk.id,
        users["manager"],
    )

    assert response is not None

    assert response.continuous_risk_state == "CURRENT"
    assert response.treatment_state == "CURRENT"
    assert response.reassessment_required is False
    assert response.state_reasons == []

    alert_types = _alert_types(response)

    assert "RISK_STATE_DEGRADED" not in alert_types
    assert "RISK_REASSESSMENT_REQUIRED" not in alert_types


def test_phase56_monitoring_degraded_risk_emits_state_alert(
    db,
    users,
):
    risk = _risk(
        db,
        users,
        score=12,
    )

    _treatment(
        db,
        users,
        risk,
    )

    control = _control(
        db,
        users,
    )

    _connect_control(
        db,
        risk,
        control,
    )

    audit = _audit(
        db,
        users,
    )

    _finding(
        db,
        audit,
        control,
        severity="High",
        status="Open",
    )

    state = get_continuous_risk_state(
        db,
        risk,
    )

    assert state.risk_state.value == "DEGRADED"

    response = get_risk_monitoring(
        db,
        risk.id,
        users["manager"],
    )

    assert response is not None
    assert response.continuous_risk_state == "DEGRADED"
    assert response.reassessment_required is False

    alert_types = _alert_types(response)

    assert "RISK_STATE_DEGRADED" in alert_types
    assert "RISK_REASSESSMENT_REQUIRED" not in alert_types


def test_phase56_monitoring_reassessment_required_emits_state_alert(
    db,
    users,
):
    risk = _risk(
        db,
        users,
        score=12,
    )

    # No authoritative treatment.
    response = get_risk_monitoring(
        db,
        risk.id,
        users["manager"],
    )

    assert response is not None
    assert response.continuous_risk_state == "REASSESSMENT_REQUIRED"
    assert response.treatment_state == "REQUIRES_REASSESSMENT"
    assert response.reassessment_required is True

    alert_types = _alert_types(response)

    assert "RISK_REASSESSMENT_REQUIRED" in alert_types
    assert "RISK_STATE_DEGRADED" not in alert_types

    reassessment_alerts = [
        alert
        for alert in response.alerts
        if alert.alert_type == "RISK_REASSESSMENT_REQUIRED"
    ]

    assert len(reassessment_alerts) == 1
    assert reassessment_alerts[0].severity == "CRITICAL"
    assert reassessment_alerts[0].resource_type == "risk"
    assert reassessment_alerts[0].resource_id == risk.id


def test_phase56_monitoring_exposes_state_reasons(
    db,
    users,
):
    risk = _risk(
        db,
        users,
        score=12,
    )

    _treatment(
        db,
        users,
        risk,
    )

    control = _control(
        db,
        users,
    )

    _connect_control(
        db,
        risk,
        control,
    )

    audit = _audit(
        db,
        users,
    )

    _finding(
        db,
        audit,
        control,
        severity="High",
        status="Open",
    )

    response = get_risk_monitoring(
        db,
        risk.id,
        users["manager"],
    )

    assert response is not None
    assert response.continuous_risk_state == "DEGRADED"
    assert response.state_reasons

    reason_codes = {
        reason["code"]
        for reason in response.state_reasons
    }

    assert "OPEN_HIGH_FINDING" in reason_codes

    reason = next(
        reason
        for reason in response.state_reasons
        if reason["code"] == "OPEN_HIGH_FINDING"
    )

    assert reason["severity"] == "HIGH"
    assert reason["resource_type"] == "audit_finding"


def test_phase56_monitoring_overview_counts_degraded_and_reassessment(
    db,
    users,
):
    degraded_risk = _risk(
        db,
        users,
        score=12,
    )

    _treatment(
        db,
        users,
        degraded_risk,
    )

    control = _control(
        db,
        users,
    )

    _connect_control(
        db,
        degraded_risk,
        control,
    )

    audit = _audit(
        db,
        users,
    )

    _finding(
        db,
        audit,
        control,
        severity="High",
        status="Open",
    )

    reassessment_risk = _risk(
        db,
        users,
        score=12,
    )

    # No authoritative treatment.
    response = get_monitoring_overview(
        db,
        users["manager"],
    )

    assert response.metrics.degraded_risks >= 1
    assert response.metrics.reassessment_required_risks >= 1


def test_phase56_monitoring_state_alerts_coexist_with_existing_alerts(
    db,
    users,
):
    risk = _risk(
        db,
        users,
        score=20,
    )

    # No authoritative treatment means reassessment is required.
    response = get_risk_monitoring(
        db,
        risk.id,
        users["manager"],
    )

    assert response is not None

    alert_types = _alert_types(response)

    # Existing Phase 55/46 monitoring remains present.
    assert "CRITICAL_RISK" in alert_types

    # New Phase 56 state alert is also present.
    assert "RISK_REASSESSMENT_REQUIRED" in alert_types

    assert len(response.alerts) >= 2


def test_phase56_monitoring_treatment_drift_emits_state_alert(
    db,
    users,
):
    risk = _risk(
        db,
        users,
        score=12,
    )

    _treatment(
        db,
        users,
        risk,
        status="In Progress",
        target_date=date(2026, 9, 1),
    )

    response = get_risk_monitoring(
        db,
        risk.id,
        users["manager"],
    )

    assert response is not None

    assert response.continuous_risk_state == "DEGRADED"
    assert response.treatment_state == "DEGRADED"
    assert response.reassessment_required is False

    alert_types = _alert_types(response)

    # Existing monitoring alert remains.
    assert "OVERDUE_RISK_TREATMENT" in alert_types

    # New Phase 56 state alert is also present.
    assert "RISK_STATE_DEGRADED" in alert_types


def test_phase56_monitoring_visibility_boundary(
    db,
    users,
):
    risk = Risk(
        title="Phase 56 Out Of Scope Risk",
        description="Risk outside manager visibility.",
        likelihood=3,
        impact=4,
        risk_score=12,
        status="Open",
        owner_id=users["admin"].id,
        created_by_id=users["admin"].id,
    )

    db.add(risk)
    db.commit()
    db.refresh(risk)

    response = get_risk_monitoring(
        db,
        risk.id,
        users["manager"],
    )

    assert response is None


def test_phase56_monitoring_state_matches_state_service(
    db,
    users,
):
    risk = _risk(
        db,
        users,
        score=12,
    )

    _treatment(
        db,
        users,
        risk,
    )

    expected = get_continuous_risk_state(
        db,
        risk,
    )

    response = get_risk_monitoring(
        db,
        risk.id,
        users["manager"],
    )

    assert response is not None

    assert response.continuous_risk_state == (
        expected.risk_state.value
    )

    assert response.treatment_state == (
        expected.treatment_state.value
    )

    assert response.reassessment_required == (
        expected.reassessment_required
    )

    assert [
        reason["code"]
        for reason in response.state_reasons
    ] == [
        reason.code.value
        for reason in expected.reasons
    ]