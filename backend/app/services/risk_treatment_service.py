from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.risk_treatment import RiskTreatment
from app.schemas.risk_treatment import (
    RiskTreatmentCreate,
    RiskTreatmentUpdate,
)
from app.models.user import User


# ==========================================================
# CONSTANTS
# ==========================================================

APPROVAL_STATUSES = {
    "Approved",
    "Rejected",
}

OPEN_ACCEPTANCE_STATUSES = {
    "Pending",
}

NO_ACCEPTANCE_STATUS = "Not Required"

# Valid lifecycle transitions. A treatment may move forward through the
# workflow, but terminal states cannot be reopened implicitly.
VALID_STATUS_TRANSITIONS = {
    "Planned": {"Planned", "In Progress", "Cancelled"},
    "In Progress": {"In Progress", "Completed", "Cancelled"},
    "Completed": {"Completed"},
    "Cancelled": {"Cancelled"},
}

TERMINAL_ACCEPTANCE_STATUSES = {
    "Approved",
    "Rejected",
}


# ==========================================================
# INTERNAL VALIDATION
# ==========================================================

def _validate_treatment_state(
    *,
    strategy: str,
    status: str,
    treatment_plan: str,
    owner_id: int,
    residual_likelihood: int | None,
    residual_impact: int | None,
    residual_risk_score: int | None,
    acceptance_status: str,
    acceptance_reason: str | None,
    accepted_by_id: int | None,
    accepted_at,
):
    if not treatment_plan or len(treatment_plan.strip()) < 10:
        raise ValueError(
            "Treatment plan must contain at least 10 characters."
        )

    if owner_id < 1:
        raise ValueError(
            "Treatment owner is invalid."
        )

    residual_values = (
        residual_likelihood,
        residual_impact,
        residual_risk_score,
    )

    provided_residual_values = sum(
        value is not None
        for value in residual_values
    )

    if (
        provided_residual_values != 0
        and provided_residual_values != 3
    ):
        raise ValueError(
            "Residual risk assessment must include "
            "residual_likelihood, residual_impact, "
            "and residual_risk_score together."
        )

    if (
        residual_likelihood is not None
        and residual_impact is not None
        and residual_risk_score is not None
    ):
        expected_score = (
            residual_likelihood
            * residual_impact
        )

        if residual_risk_score != expected_score:
            raise ValueError(
                "residual_risk_score must equal "
                "residual_likelihood multiplied by "
                "residual_impact."
            )

    # ------------------------------------------------------
    # Acceptance rules
    # ------------------------------------------------------

    if strategy != "Accept":

        if acceptance_status != NO_ACCEPTANCE_STATUS:
            raise ValueError(
                "Acceptance status is only applicable "
                "to the Accept treatment strategy."
            )

        if (
            acceptance_reason is not None
            or accepted_by_id is not None
            or accepted_at is not None
        ):
            raise ValueError(
                "Acceptance details are only applicable "
                "to the Accept treatment strategy."
            )

        return

    # Accept strategy requires an actual acceptance workflow.
    if acceptance_status == NO_ACCEPTANCE_STATUS:
        raise ValueError(
            "Accept treatment strategy requires "
            "an acceptance status."
        )

    if acceptance_status == "Pending":

        if (
            accepted_by_id is not None
            or accepted_at is not None
        ):
            raise ValueError(
                "Pending acceptance cannot contain "
                "approval metadata."
            )

    elif acceptance_status in APPROVAL_STATUSES:

        if accepted_by_id is None:
            raise ValueError(
                "Approved or rejected acceptance requires "
                "accepted_by_id."
            )

        if accepted_at is None:
            raise ValueError(
                "Approved or rejected acceptance requires "
                "accepted_at."
            )

    else:
        raise ValueError(
            "Invalid acceptance status."
        )


# ==========================================================
# CREATE
# ==========================================================

def create_risk_treatment(
    db: Session,
    treatment_data: RiskTreatmentCreate,
    current_user: User,
):
    """
    Create a risk treatment.

    Approval metadata is always attributed to the authenticated
    user by the API layer when an approval/rejection is allowed.
    """

    treatment = RiskTreatment(
        risk_id=treatment_data.risk_id,
        strategy=treatment_data.strategy.value,
        status=treatment_data.status.value,
        treatment_plan=treatment_data.treatment_plan,
        owner_id=treatment_data.owner_id,
        target_date=treatment_data.target_date,
        residual_likelihood=treatment_data.residual_likelihood,
        residual_impact=treatment_data.residual_impact,
        residual_risk_score=treatment_data.residual_risk_score,
        acceptance_status=treatment_data.acceptance_status.value,
        acceptance_reason=treatment_data.acceptance_reason,
        accepted_by_id=treatment_data.accepted_by_id,
        accepted_at=treatment_data.accepted_at,
    )

    _validate_treatment_state(
        strategy=treatment.strategy,
        status=treatment.status,
        treatment_plan=treatment.treatment_plan,
        owner_id=treatment.owner_id,
        residual_likelihood=treatment.residual_likelihood,
        residual_impact=treatment.residual_impact,
        residual_risk_score=treatment.residual_risk_score,
        acceptance_status=treatment.acceptance_status,
        acceptance_reason=treatment.acceptance_reason,
        accepted_by_id=treatment.accepted_by_id,
        accepted_at=treatment.accepted_at,
    )

    db.add(treatment)
    db.commit()
    db.refresh(treatment)

    return treatment


# ==========================================================
# UPDATE
# ==========================================================

def update_risk_treatment(
    db: Session,
    treatment: RiskTreatment,
    treatment_data: RiskTreatmentUpdate,
    current_user_id: int,
    allow_approval: bool,
):
    """
    Update a risk treatment while validating the complete
    resulting state before committing.
    """

    new_strategy = (
        treatment_data.strategy.value
        if treatment_data.strategy is not None
        else treatment.strategy
    )

    new_status = (
        treatment_data.status.value
        if treatment_data.status is not None
        else treatment.status
    )

    new_plan = (
        treatment_data.treatment_plan
        if treatment_data.treatment_plan is not None
        else treatment.treatment_plan
    )

    new_owner_id = (
        treatment_data.owner_id
        if treatment_data.owner_id is not None
        else treatment.owner_id
    )

    new_target_date = (
        treatment_data.target_date
        if treatment_data.target_date is not None
        else treatment.target_date
    )

    new_residual_likelihood = (
        treatment_data.residual_likelihood
        if treatment_data.residual_likelihood is not None
        else treatment.residual_likelihood
    )

    new_residual_impact = (
        treatment_data.residual_impact
        if treatment_data.residual_impact is not None
        else treatment.residual_impact
    )

    new_residual_risk_score = (
        treatment_data.residual_risk_score
        if treatment_data.residual_risk_score is not None
        else treatment.residual_risk_score
    )

    new_acceptance_status = (
        treatment_data.acceptance_status.value
        if treatment_data.acceptance_status is not None
        else treatment.acceptance_status
    )

    new_acceptance_reason = (
        treatment_data.acceptance_reason
        if treatment_data.acceptance_reason is not None
        else treatment.acceptance_reason
    )

    new_accepted_by_id = (
        treatment.accepted_by_id
    )

    new_accepted_at = (
        treatment.accepted_at
    )

    # ------------------------------------------------------
    # Lifecycle transition
    # ------------------------------------------------------

    allowed_statuses = VALID_STATUS_TRANSITIONS.get(
        treatment.status,
        {treatment.status},
    )

    if new_status not in allowed_statuses:
        raise ValueError(
            f"Invalid risk treatment status transition: "
            f"{treatment.status} -> {new_status}."
        )

    # ------------------------------------------------------
    # Strategy change
    # ------------------------------------------------------

    # A finalized acceptance decision is immutable. In particular, a
    # finalized Accept treatment must not be converted to another strategy
    # as a way to silently clear its approval/rejection record.
    if (
        treatment.acceptance_status in TERMINAL_ACCEPTANCE_STATUSES
        and treatment_data.strategy is not None
        and new_strategy != treatment.strategy
    ):
        raise PermissionError(
            "A finalized risk acceptance decision cannot change treatment strategy."
        )

    if new_strategy != "Accept":
        new_acceptance_status = NO_ACCEPTANCE_STATUS
        new_acceptance_reason = None
        new_accepted_by_id = None
        new_accepted_at = None

    # ------------------------------------------------------
    # Acceptance immutability
    # ------------------------------------------------------

    if treatment.acceptance_status in TERMINAL_ACCEPTANCE_STATUSES:
        if (
            treatment_data.acceptance_status is not None
            and new_acceptance_status != treatment.acceptance_status
        ):
            raise PermissionError(
                "A finalized risk acceptance decision cannot be changed."
            )

        if (
            treatment_data.acceptance_reason is not None
            and treatment_data.acceptance_reason
            != treatment.acceptance_reason
        ):
            raise PermissionError(
                "The acceptance reason cannot be changed after a final decision."
            )

    # ------------------------------------------------------
    # Acceptance transition
    # ------------------------------------------------------

    if treatment_data.acceptance_status is not None:

        if new_acceptance_status == "Pending":

            new_accepted_by_id = None
            new_accepted_at = None

        elif new_acceptance_status in APPROVAL_STATUSES:

            if not allow_approval:
                raise PermissionError(
                    "You are not authorized to approve or "
                    "reject risk acceptance."
                )

            new_accepted_by_id = current_user_id
            new_accepted_at = datetime.now(
                timezone.utc
            )

        elif new_acceptance_status == NO_ACCEPTANCE_STATUS:

            new_accepted_by_id = None
            new_accepted_at = None

    if (
        new_strategy == "Accept"
        and new_acceptance_status in TERMINAL_ACCEPTANCE_STATUSES
    ):
        # A final approval/rejection must carry an explicit reason in the
        # decision request. A reason that happened to exist while the
        # treatment was Pending must not silently become the final decision
        # rationale.
        if (
            treatment_data.acceptance_status is not None
            and treatment.acceptance_status not in TERMINAL_ACCEPTANCE_STATUSES
            and (
                treatment_data.acceptance_reason is None
                or not treatment_data.acceptance_reason.strip()
            )
        ):
            raise ValueError(
                "A final risk acceptance decision requires an acceptance_reason."
            )

        if (
            new_acceptance_reason is None
            or not new_acceptance_reason.strip()
        ):
            raise ValueError(
                "A final risk acceptance decision requires an acceptance_reason."
            )

    _validate_treatment_state(
        strategy=new_strategy,
        status=new_status,
        treatment_plan=new_plan,
        owner_id=new_owner_id,
        residual_likelihood=new_residual_likelihood,
        residual_impact=new_residual_impact,
        residual_risk_score=new_residual_risk_score,
        acceptance_status=new_acceptance_status,
        acceptance_reason=new_acceptance_reason,
        accepted_by_id=new_accepted_by_id,
        accepted_at=new_accepted_at,
    )

    # ------------------------------------------------------
    # Apply state
    # ------------------------------------------------------

    treatment.strategy = new_strategy
    treatment.status = new_status
    treatment.treatment_plan = new_plan
    treatment.owner_id = new_owner_id
    treatment.target_date = new_target_date
    treatment.residual_likelihood = (
        new_residual_likelihood
    )
    treatment.residual_impact = (
        new_residual_impact
    )
    treatment.residual_risk_score = (
        new_residual_risk_score
    )
    treatment.acceptance_status = (
        new_acceptance_status
    )
    treatment.acceptance_reason = (
        new_acceptance_reason
    )
    treatment.accepted_by_id = (
        new_accepted_by_id
    )
    treatment.accepted_at = (
        new_accepted_at
    )

    db.commit()
    db.refresh(treatment)

    return treatment


# ==========================================================
# DELETE
# ==========================================================

def delete_risk_treatment(
    db: Session,
    treatment: RiskTreatment,
):
    db.delete(treatment)
    db.commit()

    return True