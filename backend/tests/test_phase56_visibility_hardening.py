from datetime import date, datetime, timezone

from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.control import Control
from app.models.evidence import Evidence
from app.models.framework import Framework
from app.models.risk import Risk
from app.models.risk_control import RiskControl
from app.models.risk_treatment import RiskTreatment

from app.services.continuous_risk_state_service import (
    get_continuous_risk_state,
)


def _risk(
    db,
    users,
):
    risk = Risk(
        title="Phase 56 Visibility Risk",
        description="Visibility hardening test risk.",
        likelihood=3,
        impact=4,
        risk_score=12,
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
    owner_id,
    status="Completed",
    residual_likelihood=2,
    residual_impact=3,
):
    treatment = RiskTreatment(
        risk_id=risk.id,
        strategy="Mitigate",
        status=status,
        treatment_plan="Visibility test treatment.",
        owner_id=owner_id,
        target_date=date(2026, 12, 31),
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
    owner_id,
):
    control = Control(
        title="Phase 56 Visibility Control",
        description="Visibility test control.",
        control_type="Preventive",
        status="Active",
        effectiveness=80,
        owner_id=owner_id,
        created_by_id=owner_id,
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


def _evidence(
    db,
    users,
    control,
):
    evidence = Evidence(
        control_id=control.id,
        title="Visible Supporting Evidence",
        description="Fresh evidence for the visibility hardening test.",
        file_name="visibility-test.pdf",
        file_path="/test/visibility-test.pdf",
        uploaded_by=users["analyst"].id,
        uploaded_at=datetime(
            2026,
            9,
            27,
            tzinfo=timezone.utc,
        ),
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return evidence


def _audit(
    db,
    users,
    *,
    auditor_id,
):
    framework = Framework(
        name="Phase 56 Visibility Framework",
        version="1.0",
        description="Visibility hardening framework.",
    )

    db.add(framework)
    db.commit()
    db.refresh(framework)

    audit = Audit(
        name="Phase 56 Visibility Audit",
        framework_id=framework.id,
        auditor_id=auditor_id,
        created_by_id=auditor_id,
        scope="Organization",
        status="Completed",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )

    db.add(audit)
    db.commit()
    db.refresh(audit)

    return audit


def test_hidden_treatment_cannot_change_visible_risk_state(
    db,
    users,
):
    risk = _risk(
        db,
        users,
    )

    visible_treatment = _treatment(
        db,
        users,
        risk,
        owner_id=users["analyst"].id,
        status="Completed",
        residual_likelihood=2,
        residual_impact=3,
    )

    hidden_treatment = _treatment(
        db,
        users,
        risk,
        owner_id=users["admin"].id,
        status="Completed",
        residual_likelihood=5,
        residual_impact=5,
    )

    now = datetime.now(timezone.utc)

    visible_treatment.updated_at = now
    hidden_treatment.updated_at = now.replace(
        microsecond=now.microsecond + 1
    )

    db.commit()

    state = get_continuous_risk_state(
        db,
        risk,
        current_user=users["manager"],
        today=date(2026, 9, 27),
    )

    assert state.risk_state.value == "CURRENT"
    assert state.treatment_state.value == "CURRENT"
    assert state.reassessment_required is False

    assert (
        state.selected_treatment_id
        == visible_treatment.id
    )

    assert state.residual_risk_score == 6

    assert state.reasons == []


def test_hidden_finding_cannot_change_visible_risk_state(
    db,
    users,
):
    risk = _risk(
        db,
        users,
    )

    _treatment(
        db,
        users,
        risk,
        owner_id=users["analyst"].id,
    )

    control = _control(
        db,
        users,
        owner_id=users["analyst"].id,
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
    )

    hidden_audit = _audit(
        db,
        users,
        auditor_id=users["admin"].id,
    )

    hidden_finding = AuditFinding(
        audit_id=hidden_audit.id,
        control_id=control.id,
        title="Hidden Critical Finding",
        description="This finding must not affect manager state.",
        severity="Critical",
        recommendation="Remediate.",
        status="Open",
    )

    db.add(hidden_finding)
    db.commit()

    state = get_continuous_risk_state(
        db,
        risk,
        current_user=users["manager"],
        today=date(2026, 9, 27),
    )

    assert state.risk_state.value == "CURRENT"
    assert state.treatment_state.value == "CURRENT"
    assert state.reassessment_required is False

    reason_codes = {
        reason.code.value
        for reason in state.reasons
    }

    assert "OPEN_CRITICAL_FINDING" not in reason_codes
    assert "OPEN_HIGH_FINDING" not in reason_codes