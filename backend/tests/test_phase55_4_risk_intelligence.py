from datetime import date

from app.models.risk_treatment import RiskTreatment
from app.services.grc_intelligence_service import (
    get_risk_intelligence,
)


def _treatment(
    *,
    risk_id,
    owner_id,
    strategy="Mitigate",
    status="Completed",
    residual_likelihood=2,
    residual_impact=3,
    acceptance_status="Not Required",
    accepted_by_id=None,
    accepted_at=None,
):
    score = (
        residual_likelihood * residual_impact
        if residual_likelihood is not None
        and residual_impact is not None
        else None
    )

    return RiskTreatment(
        risk_id=risk_id,
        strategy=strategy,
        status=status,
        treatment_plan=(
            "Implement and maintain the treatment plan "
            "with documented management oversight."
        ),
        owner_id=owner_id,
        target_date=date(2026, 12, 31),
        residual_likelihood=residual_likelihood,
        residual_impact=residual_impact,
        residual_risk_score=score,
        acceptance_status=acceptance_status,
        accepted_by_id=accepted_by_id,
        accepted_at=accepted_at,
    )


# ==========================================================
# 55.4.1A — BASELINE
# ==========================================================

def test_intelligence_without_treatment_preserves_control_estimate(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["analyst"]

    result = get_risk_intelligence(
        db,
        risk.id,
        users["analyst"],
    )

    assert result is not None

    assert result.metrics.treatment_count == 0

    assert (
        result.metrics.effective_treatment_count
        == 0
    )

    assert (
        result.metrics.treatment_residual_risk
        is None
    )

    assert (
        result.metrics.treatment_aware_residual_risk
        == result.metrics.control_estimated_residual_risk
    )

    assert (
        result.metrics.estimated_residual_risk
        == result.metrics.control_estimated_residual_risk
    )


# ==========================================================
# 55.4.1B — COMPLETED TREATMENT
# ==========================================================

def test_completed_treatment_becomes_treatment_aware_residual(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["analyst"]

    treatment = _treatment(
        risk_id=risk.id,
        owner_id=users["analyst"].id,
        status="Completed",
        residual_likelihood=2,
        residual_impact=3,
    )

    db.add(treatment)
    db.commit()
    db.refresh(treatment)

    result = get_risk_intelligence(
        db,
        risk.id,
        users["analyst"],
    )

    assert result is not None

    assert result.metrics.treatment_count == 1

    assert (
        result.metrics.effective_treatment_count
        == 1
    )

    assert (
        result.metrics.treatment_residual_risk
        == 6.0
    )

    assert (
        result.metrics.treatment_aware_residual_risk
        == 6.0
    )

    assert (
        result.metrics.estimated_residual_risk
        == 6.0
    )

    assert (
        result.metrics.selected_treatment_id
        == treatment.id
    )


# ==========================================================
# 55.4.1C — PLANNED
# ==========================================================

def test_planned_treatment_does_not_change_residual_risk(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["analyst"]

    treatment = _treatment(
        risk_id=risk.id,
        owner_id=users["analyst"].id,
        status="Planned",
        residual_likelihood=1,
        residual_impact=1,
    )

    db.add(treatment)
    db.commit()

    result = get_risk_intelligence(
        db,
        risk.id,
        users["analyst"],
    )

    assert result is not None

    assert result.metrics.treatment_count == 1

    assert (
        result.metrics.effective_treatment_count
        == 0
    )

    assert (
        result.metrics.treatment_residual_risk
        is None
    )

    assert (
        result.metrics.estimated_residual_risk
        == result.metrics.control_estimated_residual_risk
    )


# ==========================================================
# 55.4.1D — CANCELLED
# ==========================================================

def test_cancelled_treatment_does_not_change_residual_risk(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["analyst"]

    treatment = _treatment(
        risk_id=risk.id,
        owner_id=users["analyst"].id,
        status="Cancelled",
        residual_likelihood=1,
        residual_impact=1,
    )

    db.add(treatment)
    db.commit()

    result = get_risk_intelligence(
        db,
        risk.id,
        users["analyst"],
    )

    assert result is not None

    assert (
        result.metrics.effective_treatment_count
        == 0
    )

    assert (
        result.metrics.treatment_residual_risk
        is None
    )


# ==========================================================
# 55.4.1E — IN PROGRESS
# ==========================================================

def test_in_progress_treatment_is_used_when_no_completed_treatment_exists(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["analyst"]

    treatment = _treatment(
        risk_id=risk.id,
        owner_id=users["analyst"].id,
        status="In Progress",
        residual_likelihood=3,
        residual_impact=2,
    )

    db.add(treatment)
    db.commit()
    db.refresh(treatment)

    result = get_risk_intelligence(
        db,
        risk.id,
        users["analyst"],
    )

    assert result.metrics.treatment_residual_risk == 6.0

    assert (
        result.metrics.selected_treatment_id
        == treatment.id
    )


# ==========================================================
# 55.4.1F — LIFECYCLE PRIORITY
# ==========================================================

def test_completed_treatment_takes_precedence_over_in_progress(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["analyst"]

    in_progress = _treatment(
        risk_id=risk.id,
        owner_id=users["analyst"].id,
        status="In Progress",
        residual_likelihood=1,
        residual_impact=1,
    )

    completed = _treatment(
        risk_id=risk.id,
        owner_id=users["analyst"].id,
        status="Completed",
        residual_likelihood=4,
        residual_impact=4,
    )

    db.add_all([
        in_progress,
        completed,
    ])

    db.commit()
    db.refresh(completed)

    result = get_risk_intelligence(
        db,
        risk.id,
        users["analyst"],
    )

    assert (
        result.metrics.treatment_residual_risk
        == 16.0
    )

    assert (
        result.metrics.selected_treatment_id
        == completed.id
    )


# ==========================================================
# 55.4.1G — MULTIPLE TREATMENTS
# ==========================================================

def test_multiple_completed_treatments_use_latest_updated_assessment(
    db,
    users,
    resource_data,
):
    from datetime import datetime, timezone

    risk = resource_data["risks"]["analyst"]

    older = _treatment(
        risk_id=risk.id,
        owner_id=users["analyst"].id,
        status="Completed",
        residual_likelihood=4,
        residual_impact=4,
    )

    newer = _treatment(
        risk_id=risk.id,
        owner_id=users["analyst"].id,
        status="Completed",
        residual_likelihood=2,
        residual_impact=2,
    )

    db.add_all([
        older,
        newer,
    ])

    db.commit()

    db.refresh(older)
    db.refresh(newer)

    older.updated_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    newer.updated_at = datetime(
        2026,
        2,
        1,
        tzinfo=timezone.utc,
    )

    db.commit()

    result = get_risk_intelligence(
        db,
        risk.id,
        users["analyst"],
    )

    assert (
        result.metrics.treatment_residual_risk
        == 4.0
    )

    assert (
        result.metrics.selected_treatment_id
        == newer.id
    )


# ==========================================================
# 55.4.1H — ACCEPT / APPROVED
# ==========================================================

def test_approved_accept_treatment_can_supply_residual_risk(
    db,
    users,
    resource_data,
):
    from datetime import datetime, timezone

    risk = resource_data["risks"]["analyst"]

    treatment = _treatment(
        risk_id=risk.id,
        owner_id=users["analyst"].id,
        strategy="Accept",
        status="Completed",
        residual_likelihood=3,
        residual_impact=3,
        acceptance_status="Approved",
        accepted_by_id=users["manager"].id,
        accepted_at=datetime.now(
            timezone.utc
        ),
    )

    db.add(treatment)
    db.commit()
    db.refresh(treatment)

    result = get_risk_intelligence(
        db,
        risk.id,
        users["analyst"],
    )

    assert (
        result.metrics.treatment_residual_risk
        == 9.0
    )

    assert (
        result.metrics.selected_treatment_id
        == treatment.id
    )


# ==========================================================
# 55.4.1I — ACCEPT / PENDING
# ==========================================================

def test_pending_accept_treatment_does_not_affect_intelligence(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["analyst"]

    treatment = _treatment(
        risk_id=risk.id,
        owner_id=users["analyst"].id,
        strategy="Accept",
        status="In Progress",
        residual_likelihood=1,
        residual_impact=1,
        acceptance_status="Pending",
    )

    db.add(treatment)
    db.commit()

    result = get_risk_intelligence(
        db,
        risk.id,
        users["analyst"],
    )

    assert (
        result.metrics.treatment_residual_risk
        is None
    )

    assert (
        result.metrics.effective_treatment_count
        == 0
    )

    assert (
        result.metrics.estimated_residual_risk
        == result.metrics.control_estimated_residual_risk
    )


# ==========================================================
# 55.4.1J — AUTHORIZATION
# ==========================================================

def test_hidden_risk_treatments_are_not_processed(
    db,
    users,
    resource_data,
):
    hidden_risk = resource_data["risks"]["admin"]

    treatment = _treatment(
        risk_id=hidden_risk.id,
        owner_id=users["admin"].id,
        residual_likelihood=1,
        residual_impact=1,
    )

    db.add(treatment)
    db.commit()

    result = get_risk_intelligence(
        db,
        hidden_risk.id,
        users["analyst"],
    )

    assert result is None