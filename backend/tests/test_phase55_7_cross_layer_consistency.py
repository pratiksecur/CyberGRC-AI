from datetime import datetime, timezone

from app.models.risk import Risk
from app.models.risk_treatment import RiskTreatment

from app.services.grc_intelligence_service import (
    get_risk_intelligence,
)
from app.services.grc_monitoring_service import (
    get_risk_monitoring,
)
from app.services.reports_service import (
    get_risk_report,
)
from app.services.risk_treatment_residual_service import (
    select_authoritative_treatment,
)


def _risk(
    db,
    users,
    *,
    score=20,
):
    user = users["analyst"]

    risk = Risk(
        title="Phase 55.7 Cross-Layer Risk",
        description="Risk used for Phase 55.7 consistency tests.",
        likelihood=4,
        impact=5,
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
    strategy="Mitigate",
    status="Completed",
    residual_likelihood=2,
    residual_impact=3,
    acceptance_status="Not Required",
    updated_at=None,
):
    treatment = RiskTreatment(
        risk_id=risk.id,
        strategy=strategy,
        status=status,
        treatment_plan="Maintain the documented treatment plan.",
        owner_id=users["analyst"].id,
        target_date=datetime(
            2026,
            12,
            31,
        ).date(),
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
        acceptance_status=acceptance_status,
        accepted_by_id=(
            users["manager"].id
            if acceptance_status == "Approved"
            else None
        ),
        accepted_at=(
            datetime.now(timezone.utc)
            if acceptance_status == "Approved"
            else None
        ),
        updated_at=updated_at,
    )

    db.add(treatment)
    db.commit()
    db.refresh(treatment)

    return treatment


def test_phase55_7_intelligence_and_report_select_same_treatment(
    db,
    users,
):
    risk = _risk(
        db,
        users,
    )

    treatment = _treatment(
        db,
        users,
        risk,
        residual_likelihood=2,
        residual_impact=3,
    )

    intelligence = get_risk_intelligence(
        db,
        risk.id,
        users["manager"],
    )

    report = get_risk_report(
        db,
        [
            users["manager"].id,
            users["analyst"].id,
        ],
    )

    item = next(
        item
        for item in report["risks"]
        if item["id"] == risk.id
    )

    assert intelligence is not None

    assert (
        intelligence.metrics.selected_treatment_id
        == treatment.id
    )

    assert (
        intelligence.metrics.treatment_aware_residual_risk
        == 6.0
    )

    assert (
        item["selected_treatment_id"]
        == treatment.id
    )

    assert (
        item["treatment_aware_residual_risk"]
        == 6.0
    )

    assert (
        intelligence.metrics.control_estimated_residual_risk
        == item["control_estimated_residual_risk"]
    )


def test_phase55_7_pending_and_cancelled_treatments_are_ignored_consistently(
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
        status="Planned",
        residual_likelihood=1,
        residual_impact=1,
    )

    _treatment(
        db,
        users,
        risk,
        status="Cancelled",
        residual_likelihood=1,
        residual_impact=1,
    )

    intelligence = get_risk_intelligence(
        db,
        risk.id,
        users["manager"],
    )

    report = get_risk_report(
        db,
        [
            users["manager"].id,
            users["analyst"].id,
        ],
    )

    item = next(
        item
        for item in report["risks"]
        if item["id"] == risk.id
    )

    assert (
        intelligence.metrics.selected_treatment_id
        is None
    )

    assert (
        intelligence.metrics.treatment_residual_risk
        is None
    )

    assert (
        intelligence.metrics.treatment_aware_residual_risk
        == intelligence.metrics.control_estimated_residual_risk
    )

    assert (
        item["selected_treatment_id"]
        is None
    )

    assert (
        item["treatment_residual_risk"]
        is None
    )

    assert (
        item["treatment_aware_residual_risk"]
        == item["control_estimated_residual_risk"]
    )


def test_phase55_7_approved_accept_is_consistent_across_layers(
    db,
    users,
):
    risk = _risk(
        db,
        users,
    )

    treatment = _treatment(
        db,
        users,
        risk,
        strategy="Accept",
        status="Completed",
        residual_likelihood=2,
        residual_impact=2,
        acceptance_status="Approved",
    )

    selected = select_authoritative_treatment(
        [treatment]
    )

    intelligence = get_risk_intelligence(
        db,
        risk.id,
        users["manager"],
    )

    report = get_risk_report(
        db,
        [
            users["manager"].id,
            users["analyst"].id,
        ],
    )

    item = next(
        item
        for item in report["risks"]
        if item["id"] == risk.id
    )

    assert selected is not None
    assert selected.id == treatment.id

    assert (
        intelligence.metrics.selected_treatment_id
        == treatment.id
    )

    assert (
        intelligence.metrics.treatment_aware_residual_risk
        == 4.0
    )

    assert (
        item["selected_treatment_id"]
        == treatment.id
    )

    assert (
        item["treatment_aware_residual_risk"]
        == 4.0
    )


def test_phase55_7_completed_beats_in_progress(
    db,
    users,
):
    risk = _risk(
        db,
        users,
    )

    in_progress = _treatment(
        db,
        users,
        risk,
        status="In Progress",
        residual_likelihood=1,
        residual_impact=1,
    )

    completed = _treatment(
        db,
        users,
        risk,
        status="Completed",
        residual_likelihood=3,
        residual_impact=3,
    )

    selected = select_authoritative_treatment(
        [
            in_progress,
            completed,
        ]
    )

    assert selected is not None
    assert selected.id == completed.id


def test_phase55_7_latest_completed_assessment_wins_tie(
    db,
    users,
):
    risk = _risk(
        db,
        users,
    )

    older = _treatment(
        db,
        users,
        risk,
        status="Completed",
        residual_likelihood=3,
        residual_impact=3,
        updated_at=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    newer = _treatment(
        db,
        users,
        risk,
        status="Completed",
        residual_likelihood=2,
        residual_impact=2,
        updated_at=datetime(
            2026,
            2,
            1,
            tzinfo=timezone.utc,
        ),
    )

    selected = select_authoritative_treatment(
        [
            older,
            newer,
        ]
    )

    assert selected is not None
    assert selected.id == newer.id


def test_phase55_7_monitoring_uses_same_authoritative_treatment(
    db,
    users,
):
    risk = _risk(
        db,
        users,
    )

    in_progress = _treatment(
        db,
        users,
        risk,
        status="In Progress",
        residual_likelihood=1,
        residual_impact=1,
    )

    completed = _treatment(
        db,
        users,
        risk,
        status="Completed",
        residual_likelihood=2,
        residual_impact=2,
    )

    selected = select_authoritative_treatment(
        [
            in_progress,
            completed,
        ]
    )

    monitoring = get_risk_monitoring(
        db,
        risk.id,
        users["manager"],
    )

    assert selected is not None
    assert selected.id == completed.id

    assert monitoring is not None