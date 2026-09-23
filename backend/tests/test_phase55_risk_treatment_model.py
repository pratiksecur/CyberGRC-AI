from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.database.database import Base
from app.models.risk_treatment import RiskTreatment
from app.schemas.risk_treatment import (
    AcceptanceStatus,
    RiskTreatmentCreate,
    TreatmentStrategy,
)


def test_risk_treatment_table_is_registered():
    assert (
        RiskTreatment.__tablename__
        in Base.metadata.tables
    )


def test_risk_treatment_can_be_created_and_related(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["analyst"]
    owner = users["analyst"]

    treatment = RiskTreatment(
        risk_id=risk.id,
        strategy="Mitigate",
        status="Planned",
        treatment_plan=(
            "Implement additional security controls "
            "to reduce the identified risk."
        ),
        owner_id=owner.id,
        target_date=None,
        residual_likelihood=2,
        residual_impact=3,
        residual_risk_score=6,
        acceptance_status="Not Required",
    )

    db.add(treatment)
    db.commit()
    db.refresh(treatment)

    assert treatment.id is not None
    assert treatment.risk.id == risk.id
    assert treatment.owner.id == owner.id
    assert treatment.strategy == "Mitigate"
    assert treatment.residual_risk_score == 6


def test_risk_delete_cascades_risk_treatments(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["analyst"]

    treatment = RiskTreatment(
        risk_id=risk.id,
        strategy="Avoid",
        status="Planned",
        treatment_plan=(
            "Remove the affected process from the "
            "scope of the risk."
        ),
        owner_id=users["analyst"].id,
        acceptance_status="Not Required",
    )

    db.add(treatment)
    db.commit()
    treatment_id = treatment.id

    db.delete(risk)
    db.commit()

    deleted_treatment = (
        db.query(RiskTreatment)
        .filter(
            RiskTreatment.id == treatment_id
        )
        .first()
    )

    assert deleted_treatment is None


def test_acceptance_relationships_are_supported(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["manager"]

    treatment = RiskTreatment(
        risk_id=risk.id,
        strategy="Accept",
        status="In Progress",
        treatment_plan=(
            "Monitor the residual risk and maintain "
            "documented management oversight."
        ),
        owner_id=users["manager"].id,
        residual_likelihood=2,
        residual_impact=2,
        residual_risk_score=4,
        acceptance_status="Approved",
        acceptance_reason=(
            "Residual risk is within the approved "
            "organisational tolerance."
        ),
        accepted_by_id=users["admin"].id,
        accepted_at=datetime.now(timezone.utc),
    )

    db.add(treatment)
    db.commit()
    db.refresh(treatment)

    assert treatment.accepted_by.id == users["admin"].id
    assert (
        treatment.acceptance_status
        == "Approved"
    )


def test_residual_score_must_match_likelihood_times_impact():
    treatment = RiskTreatmentCreate(
        risk_id=1,
        strategy=TreatmentStrategy.MITIGATE,
        treatment_plan=(
            "Implement additional controls "
            "to reduce the residual risk."
        ),
        owner_id=2,
        residual_likelihood=2,
        residual_impact=4,
        residual_risk_score=8,
    )

    assert (
        treatment.residual_risk_score
        == 8
    )


def test_invalid_residual_score_is_rejected():
    with pytest.raises(
        ValidationError,
        match="residual_risk_score",
    ):
        RiskTreatmentCreate(
            risk_id=1,
            strategy=TreatmentStrategy.MITIGATE,
            treatment_plan=(
                "Implement additional controls "
                "to reduce the residual risk."
            ),
            owner_id=2,
            residual_likelihood=2,
            residual_impact=4,
            residual_risk_score=7,
        )


def test_partial_residual_assessment_is_rejected():
    with pytest.raises(
        ValidationError,
        match="Residual risk assessment",
    ):
        RiskTreatmentCreate(
            risk_id=1,
            strategy=TreatmentStrategy.MITIGATE,
            treatment_plan=(
                "Implement additional controls "
                "to reduce the residual risk."
            ),
            owner_id=2,
            residual_likelihood=2,
            residual_impact=4,
        )


def test_non_accept_strategy_cannot_use_acceptance_fields():
    with pytest.raises(
        ValidationError,
        match="Accept treatment strategy",
    ):
        RiskTreatmentCreate(
            risk_id=1,
            strategy=TreatmentStrategy.MITIGATE,
            treatment_plan=(
                "Implement additional controls "
                "to reduce the residual risk."
            ),
            owner_id=2,
            acceptance_status=(
                AcceptanceStatus.PENDING
            ),
        )


def test_approved_acceptance_requires_approval_metadata():
    with pytest.raises(
        ValidationError,
        match="accepted_by_id",
    ):
        RiskTreatmentCreate(
            risk_id=1,
            strategy=TreatmentStrategy.ACCEPT,
            treatment_plan=(
                "Monitor the residual risk and "
                "maintain management oversight."
            ),
            owner_id=2,
            acceptance_status=(
                AcceptanceStatus.APPROVED
            ),
        )