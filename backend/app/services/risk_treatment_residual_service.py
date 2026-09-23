"""Canonical risk-treatment residual-risk selection helpers.

Phase 55.7 centralizes the authoritative treatment-selection semantics so
GRC Intelligence, Monitoring, and Reports cannot silently drift apart.
"""

from datetime import datetime, timezone

from app.models.risk_treatment import RiskTreatment


# Lifecycle priority is intentionally deterministic:
#
#   0 = Completed non-Accept
#   1 = In Progress non-Accept
#   2 = Approved Accept
#
# Everything else is ineligible for residual-risk authority.
INELIGIBLE_TREATMENT_RANK = 99


def treatment_authority_rank(
    treatment: RiskTreatment,
) -> int:
    """Return the canonical treatment authority rank."""

    if (
        treatment.status == "Completed"
        and treatment.strategy != "Accept"
    ):
        return 0

    if (
        treatment.status == "In Progress"
        and treatment.strategy != "Accept"
    ):
        return 1

    if (
        treatment.strategy == "Accept"
        and treatment.acceptance_status == "Approved"
    ):
        return 2

    return INELIGIBLE_TREATMENT_RANK


def has_residual_assessment(
    treatment: RiskTreatment,
) -> bool:
    """Return whether a treatment has a complete residual assessment."""

    return (
        treatment.residual_likelihood is not None
        and treatment.residual_impact is not None
        and treatment.residual_risk_score is not None
    )


def select_authoritative_treatment(
    treatments: list[RiskTreatment],
) -> RiskTreatment | None:
    """Select exactly one authoritative treatment.

    No min/max aggregation is performed.

    Lifecycle authority is evaluated first, then:
        updated_at DESC
        created_at DESC
        id DESC

    are used as deterministic tie-breakers within the same
    lifecycle rank.
    """

    eligible = [
        treatment
        for treatment in treatments
        if (
            treatment_authority_rank(treatment)
            < INELIGIBLE_TREATMENT_RANK
        )
        and has_residual_assessment(treatment)
    ]

    if not eligible:
        return None

    best_rank = min(
        treatment_authority_rank(treatment)
        for treatment in eligible
    )

    ranked = [
        treatment
        for treatment in eligible
        if treatment_authority_rank(treatment) == best_rank
    ]

    ranked.sort(
        key=lambda treatment: (
            treatment.updated_at
            or datetime.min.replace(
                tzinfo=timezone.utc
            ),
            treatment.created_at
            or datetime.min.replace(
                tzinfo=timezone.utc
            ),
            treatment.id,
        ),
        reverse=True,
    )

    return ranked[0]