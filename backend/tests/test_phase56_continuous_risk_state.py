from datetime import date

from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.control import Control
from app.models.corrective_action import CorrectiveAction
from app.models.evidence import Evidence
from app.models.framework import Framework
from app.models.risk import Risk
from app.models.risk_control import RiskControl
from app.models.risk_treatment import RiskTreatment

from app.services.continuous_risk_state_service import (
    RiskState,
    TreatmentState,
    RiskStateReason,
    get_continuous_risk_state,
)


def _risk(
    db,
    users,
    *,
    score=12,
):
    user = users["analyst"]

    risk = Risk(
        title="Phase 56 Continuous Risk",
        description="Risk used for continuous state testing.",
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
        title="Phase 56 Control",
        description="Control used for state testing.",
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
        name="Phase 56 Framework",
        version="1.0",
        description="Framework used for Phase 56 testing.",
    )

    db.add(framework)
    db.commit()
    db.refresh(framework)

    audit = Audit(
        name="Phase 56 Audit",
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
        title="Phase 56 Finding",
        description="Finding for Phase 56 testing.",
        severity=severity,
        recommendation="Remediate the issue.",
        status=status,
    )

    db.add(finding)
    db.commit()
    db.refresh(finding)

    return finding


def _action(
    db,
    finding,
    users,
    *,
    priority="High",
    status="Open",
    due_date=None,
):
    action = CorrectiveAction(
        finding_id=finding.id,
        assigned_to=users["analyst"].id,
        title="Phase 56 Corrective Action",
        description="Corrective action for Phase 56 testing.",
        priority=priority,
        status=status,
        due_date=(
            due_date
            if due_date is not None
            else date(2026, 12, 31)
        ),
    )

    db.add(action)
    db.commit()
    db.refresh(action)

    return action


def _evidence(
    db,
    users,
    control,
    *,
    uploaded_at,
):
    evidence = Evidence(
        control_id=control.id,
        title="Phase 56 Evidence",
        description="Evidence for Phase 56 testing.",
        file_name="phase56.txt",
        file_path="uploads/phase56.txt",
        uploaded_by=users["analyst"].id,
        uploaded_at=uploaded_at,
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return evidence


def test_phase56_clean_risk_is_current(
    db,
    users,
):
    risk = _risk(db, users)

    _treatment(
        db,
        users,
        risk,
    )

    state = get_continuous_risk_state(
        db,
        risk,
        today=date(2026, 9, 27),
    )

    assert state.risk_state == RiskState.CURRENT
    assert state.treatment_state == TreatmentState.CURRENT
    assert state.reassessment_required is False
    assert state.reasons == []


def test_phase56_open_critical_finding_requires_reassessment(
    db,
    users,
):
    risk = _risk(db, users)

    treatment = _treatment(
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

    state = get_continuous_risk_state(
        db,
        risk,
        today=date(2026, 9, 27),
    )

    assert (
        state.selected_treatment_id
        == treatment.id
    )

    assert (
        state.treatment_state
        == TreatmentState.REQUIRES_REASSESSMENT
    )

    assert (
        state.risk_state
        == RiskState.REASSESSMENT_REQUIRED
    )

    assert state.reassessment_required is True

    assert any(
        reason.code
        == RiskStateReason.OPEN_CRITICAL_FINDING
        for reason in state.reasons
    )


def test_phase56_high_finding_degrades_risk(
    db,
    users,
):
    risk = _risk(db, users)

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
        today=date(2026, 9, 27),
    )

    assert state.risk_state == RiskState.DEGRADED

    assert (
        state.treatment_state
        == TreatmentState.DEGRADED
    )

    assert any(
        reason.code
        == RiskStateReason.OPEN_HIGH_FINDING
        for reason in state.reasons
    )


def test_phase56_overdue_corrective_action_degrades_risk(
    db,
    users,
):
    risk = _risk(db, users)

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

    finding = _finding(
        db,
        audit,
        control,
        severity="Medium",
        status="Open",
    )

    _action(
        db,
        finding,
        users,
        priority="High",
        status="Open",
        due_date=date(2026, 9, 1),
    )

    state = get_continuous_risk_state(
        db,
        risk,
        today=date(2026, 9, 27),
    )

    assert state.risk_state == RiskState.DEGRADED

    assert any(
        reason.code
        == RiskStateReason.OVERDUE_CORRECTIVE_ACTION
        for reason in state.reasons
    )


def test_phase56_critical_corrective_action_requires_reassessment(
    db,
    users,
):
    risk = _risk(db, users)

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

    finding = _finding(
        db,
        audit,
        control,
        severity="Medium",
        status="Open",
    )

    _action(
        db,
        finding,
        users,
        priority="Critical",
        status="Open",
    )

    state = get_continuous_risk_state(
        db,
        risk,
        today=date(2026, 9, 27),
    )

    assert (
        state.risk_state
        == RiskState.REASSESSMENT_REQUIRED
    )

    assert any(
        reason.code
        == RiskStateReason.CRITICAL_CORRECTIVE_ACTION_OPEN
        for reason in state.reasons
    )


def test_phase56_overdue_treatment_degrades_risk(
    db,
    users,
):
    risk = _risk(db, users)

    treatment = _treatment(
        db,
        users,
        risk,
        status="In Progress",
        target_date=date(2026, 9, 1),
    )

    state = get_continuous_risk_state(
        db,
        risk,
        today=date(2026, 9, 27),
    )

    assert (
        state.selected_treatment_id
        == treatment.id
    )

    assert (
        state.risk_state
        == RiskState.DEGRADED
    )

    assert any(
        reason.code
        == RiskStateReason.OVERDUE_TREATMENT
        for reason in state.reasons
    )


def test_phase56_low_control_effectiveness_degrades_risk(
    db,
    users,
):
    risk = _risk(db, users)

    _treatment(
        db,
        users,
        risk,
    )

    control = _control(
        db,
        users,
        effectiveness=40,
    )

    _connect_control(
        db,
        risk,
        control,
    )

    state = get_continuous_risk_state(
        db,
        risk,
        today=date(2026, 9, 27),
    )

    assert state.risk_state == RiskState.DEGRADED

    assert any(
        reason.code
        == RiskStateReason.CONTROL_EFFECTIVENESS_LOW
        for reason in state.reasons
    )


def test_phase56_inactive_control_degrades_risk(
    db,
    users,
):
    risk = _risk(db, users)

    _treatment(
        db,
        users,
        risk,
    )

    control = _control(
        db,
        users,
        effectiveness=80,
        status="Inactive",
    )

    _connect_control(
        db,
        risk,
        control,
    )

    state = get_continuous_risk_state(
        db,
        risk,
        today=date(2026, 9, 27),
    )

    assert state.risk_state == RiskState.DEGRADED

    assert any(
        reason.code
        == RiskStateReason.CONTROL_INACTIVE
        for reason in state.reasons
    )


def test_phase56_stale_evidence_degrades_risk(
    db,
    users,
):
    risk = _risk(db, users)

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

    _evidence(
        db,
        users,
        control,
        uploaded_at=date(2026, 6, 1),
    )

    state = get_continuous_risk_state(
        db,
        risk,
        today=date(2026, 9, 27),
    )

    assert state.risk_state == RiskState.DEGRADED

    assert any(
        reason.code
        == RiskStateReason.STALE_EVIDENCE
        for reason in state.reasons
    )


def test_phase56_missing_evidence_degrades_risk(
    db,
    users,
):
    risk = _risk(db, users)

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

    state = get_continuous_risk_state(
        db,
        risk,
        today=date(2026, 9, 27),
    )

    assert state.risk_state == RiskState.DEGRADED

    assert any(
        reason.code
        == RiskStateReason.MISSING_SUPPORTING_EVIDENCE
        for reason in state.reasons
    )


def test_phase56_elevated_residual_risk_degrades_risk(
    db,
    users,
):
    risk = _risk(
        db,
        users,
        score=25,
    )

    treatment = _treatment(
        db,
        users,
        risk,
        residual_likelihood=5,
        residual_impact=4,
    )

    state = get_continuous_risk_state(
        db,
        risk,
        today=date(2026, 9, 27),
    )

    assert (
        state.selected_treatment_id
        == treatment.id
    )

    assert (
        state.residual_risk_score
        == 20
    )

    assert state.risk_state == RiskState.DEGRADED

    assert any(
        reason.code
        == RiskStateReason.ELEVATED_RESIDUAL_RISK
        for reason in state.reasons
    )


def test_phase56_no_authoritative_treatment_requires_reassessment(
    db,
    users,
):
    risk = _risk(db, users)

    _treatment(
        db,
        users,
        risk,
        status="Planned",
    )

    state = get_continuous_risk_state(
        db,
        risk,
        today=date(2026, 9, 27),
    )

    assert (
        state.selected_treatment_id
        is None
    )

    assert (
        state.treatment_state
        == TreatmentState.REQUIRES_REASSESSMENT
    )

    assert (
        state.risk_state
        == RiskState.REASSESSMENT_REQUIRED
    )

    assert state.reassessment_required is True

    assert any(
        reason.code
        == RiskStateReason.TREATMENT_MISSING_RESIDUAL
        for reason in state.reasons
    )


def test_phase56_serialization_is_stable(
    db,
    users,
):
    risk = _risk(db, users)

    treatment = _treatment(
        db,
        users,
        risk,
    )

    state = get_continuous_risk_state(
        db,
        risk,
        today=date(2026, 9, 27),
    )

    payload = state.as_dict()

    assert payload["risk_id"] == risk.id
    assert payload["risk_state"] == "CURRENT"
    assert payload["treatment_state"] == "CURRENT"
    assert payload["reassessment_required"] is False
    assert (
        payload["selected_treatment_id"]
        == treatment.id
    )

    assert payload["reasons"] == []