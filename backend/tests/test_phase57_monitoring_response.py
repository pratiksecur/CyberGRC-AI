from datetime import date

from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.control import Control
from app.models.framework import Framework
from app.models.risk import Risk
from app.models.risk_control import RiskControl
from app.models.risk_treatment import RiskTreatment

from app.services.grc_monitoring_service import (
    get_monitoring_overview,
)


# ==========================================================
# HELPERS
# ==========================================================

def _risk(
    db,
    users,
    *,
    title="Phase 57 Monitoring Risk",
    score=12,
):
    risk = Risk(
        title=title,
        description="Risk used for Phase 57 monitoring response testing.",
        likelihood=3,
        impact=4,
        risk_score=score,
        status="Open",
        owner_id=users["analyst"].id,
        created_by_id=users["analyst"].id,
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
):
    treatment = RiskTreatment(
        risk_id=risk.id,
        strategy="Mitigate",
        status=status,
        treatment_plan="Maintain treatment.",
        owner_id=users["analyst"].id,
        target_date=date(2026, 12, 31),
        residual_likelihood=residual_likelihood,
        residual_impact=residual_impact,
        residual_risk_score=(
            residual_likelihood
            * residual_impact
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
    effectiveness=90,
    status="Active",
):
    control = Control(
        title="Phase 57 Monitoring Control",
        description="Control used for Phase 57 monitoring response testing.",
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
        name="Phase 57 Monitoring Framework",
        version="1.0",
        description="Framework used for Phase 57 monitoring response testing.",
    )

    db.add(framework)
    db.commit()
    db.refresh(framework)

    audit = Audit(
        name="Phase 57 Monitoring Audit",
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
    severity="Critical",
    status="Open",
):
    finding = AuditFinding(
        audit_id=audit.id,
        control_id=control.id,
        title="Phase 57 Critical Finding",
        description="Critical finding used for response testing.",
        severity=severity,
        recommendation="Remediate the issue.",
        status=status,
    )

    db.add(finding)
    db.commit()
    db.refresh(finding)

    return finding


# ==========================================================
# CURRENT → MONITOR
# ==========================================================

def test_phase57_monitoring_current_risk_has_monitor_response(
    db,
    users,
):
    risk = _risk(
        db,
        users,
        score=6,
    )

    _treatment(
        db,
        users,
        risk,
        residual_likelihood=1,
        residual_impact=5,
    )

    response = get_monitoring_overview(
        db,
        users["manager"],
    )

    risk_response = next(
        item
        for item in response.risk_responses
        if item.risk_id == risk.id
    )

    assert risk_response.risk_state == "CURRENT"
    assert risk_response.treatment_state == "CURRENT"

    assert risk_response.reassessment_required is False

    assert risk_response.response_required is False

    assert risk_response.priority == "LOW"

    assert risk_response.human_approval_required is False

    assert len(risk_response.decisions) == 1

    assert (
        risk_response.decisions[0].decision
        == "MONITOR"
    )

    assert (
        risk_response.decisions[0].priority
        == "LOW"
    )


# ==========================================================
# REASSESSMENT → REASSESS RISK
# ==========================================================

def test_phase57_monitoring_reassessment_requires_response(
    db,
    users,
):
    risk = _risk(
        db,
        users,
        score=12,
    )

    response = get_monitoring_overview(
        db,
        users["manager"],
    )

    risk_response = next(
        item
        for item in response.risk_responses
        if item.risk_id == risk.id
    )

    assert (
        risk_response.risk_state
        == "REASSESSMENT_REQUIRED"
    )

    assert (
        risk_response.treatment_state
        == "REQUIRES_REASSESSMENT"
    )

    assert risk_response.reassessment_required is True

    assert risk_response.response_required is True

    assert risk_response.priority == "HIGH"

    assert risk_response.human_approval_required is True

    assert len(risk_response.decisions) == 1

    assert (
        risk_response.decisions[0].decision
        == "REASSESS_RISK"
    )

    assert (
        risk_response.decisions[0].human_approval_required
        is True
    )


# ==========================================================
# CRITICAL ESCALATION
# ==========================================================

def test_phase57_monitoring_critical_finding_escalates(
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
        severity="Critical",
        status="Open",
    )

    response = get_monitoring_overview(
        db,
        users["manager"],
    )

    risk_response = next(
        item
        for item in response.risk_responses
        if item.risk_id == risk.id
    )

    assert risk_response.response_required is True

    assert risk_response.priority == "CRITICAL"

    assert risk_response.human_approval_required is True

    assert len(risk_response.decisions) >= 1

    escalation = next(
        decision
        for decision in risk_response.decisions
        if decision.decision == "ESCALATE"
    )

    assert escalation.priority == "CRITICAL"

    assert (
        escalation.human_approval_required
        is True
    )

    assert (
        "OPEN_CRITICAL_FINDING"
        in escalation.reason_codes
    )


# ==========================================================
# AGGREGATED COUNTS
# ==========================================================

def test_phase57_monitoring_aggregates_response_metrics(
    db,
    users,
):
    current_risk = _risk(
        db,
        users,
        title="Phase 57 Current Risk",
        score=6,
    )

    _treatment(
        db,
        users,
        current_risk,
        residual_likelihood=1,
        residual_impact=5,
    )

    reassessment_risk = _risk(
        db,
        users,
        title="Phase 57 Reassessment Risk",
        score=12,
    )

    response = get_monitoring_overview(
        db,
        users["manager"],
    )

    assert response.metrics.response_required_risks >= 1

    assert (
        response.metrics.human_approval_required_risks
        >= 1
    )

    assert (
        response.metrics.critical_response_risks
        == 0
    )

    current_response = next(
        item
        for item in response.risk_responses
        if item.risk_id == current_risk.id
    )

    reassessment_response = next(
        item
        for item in response.risk_responses
        if item.risk_id == reassessment_risk.id
    )

    assert (
        current_response.response_required
        is False
    )

    assert (
        reassessment_response.response_required
        is True
    )


# ==========================================================
# DETERMINISTIC ORDERING
# ==========================================================

def test_phase57_monitoring_response_order_is_deterministic(
    db,
    users,
):
    current_risk = _risk(
        db,
        users,
        title="Phase 57 Current",
        score=6,
    )

    _treatment(
        db,
        users,
        current_risk,
        residual_likelihood=1,
        residual_impact=5,
    )

    reassessment_risk = _risk(
        db,
        users,
        title="Phase 57 Reassessment",
        score=12,
    )

    response = get_monitoring_overview(
        db,
        users["manager"],
    )

    priorities = [
        item.priority
        for item in response.risk_responses
    ]

    priority_rank = {
        "CRITICAL": 0,
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3,
    }

    assert priorities == sorted(
        priorities,
        key=lambda value: priority_rank[value],
    )

    assert (
        response.risk_responses[-1].risk_id
        == current_risk.id
        or response.risk_responses[-1].priority
        != "LOW"
    )


# ==========================================================
# VISIBILITY
# ==========================================================

def test_phase57_monitoring_does_not_expose_out_of_scope_risk(
    db,
    users,
):
    risk = Risk(
        title="Phase 57 Out Of Scope Risk",
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

    response = get_monitoring_overview(
        db,
        users["manager"],
    )

    returned_ids = {
        item.risk_id
        for item in response.risk_responses
    }

    assert risk.id not in returned_ids