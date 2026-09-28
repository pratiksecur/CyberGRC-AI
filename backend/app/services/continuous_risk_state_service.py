"""
Continuous Risk State Service

Phase 56
--------

Deterministic, derived risk and treatment state.

This service intentionally does NOT:
- modify Risk records
- modify RiskTreatment records
- calculate a second version of residual risk
- make AI decisions
- perform authorization

It derives the current state from existing GRC data and reuses the
canonical Phase 55 authoritative treatment-selection logic.

Authorization / visibility must be enforced by the caller.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from typing import Any, Iterable, Optional

from sqlalchemy.orm import Session

from app.auth.visibility import get_visible_user_ids

from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.control import Control
from app.models.corrective_action import CorrectiveAction
from app.models.evidence import Evidence
from app.models.risk import Risk
from app.models.risk_treatment import RiskTreatment
from app.models.user import User
from app.services.risk_treatment_residual_service import (
    has_residual_assessment,
    select_authoritative_treatment,
)


# ============================================================
# State definitions
# ============================================================


class RiskState(str, Enum):
    CURRENT = "CURRENT"
    DEGRADED = "DEGRADED"
    REASSESSMENT_REQUIRED = "REASSESSMENT_REQUIRED"


class TreatmentState(str, Enum):
    CURRENT = "CURRENT"
    STALE = "STALE"
    DEGRADED = "DEGRADED"
    REQUIRES_REASSESSMENT = "REQUIRES_REASSESSMENT"


class RiskStateReason(str, Enum):
    OPEN_HIGH_FINDING = "OPEN_HIGH_FINDING"
    OPEN_CRITICAL_FINDING = "OPEN_CRITICAL_FINDING"

    OVERDUE_CORRECTIVE_ACTION = "OVERDUE_CORRECTIVE_ACTION"
    CRITICAL_CORRECTIVE_ACTION_OPEN = (
        "CRITICAL_CORRECTIVE_ACTION_OPEN"
    )

    OVERDUE_TREATMENT = "OVERDUE_TREATMENT"
    TREATMENT_CANCELLED = "TREATMENT_CANCELLED"
    TREATMENT_MISSING_RESIDUAL = (
        "TREATMENT_MISSING_RESIDUAL"
    )

    ELEVATED_RESIDUAL_RISK = "ELEVATED_RESIDUAL_RISK"

    CONTROL_INACTIVE = "CONTROL_INACTIVE"
    CONTROL_EFFECTIVENESS_LOW = "CONTROL_EFFECTIVENESS_LOW"

    STALE_EVIDENCE = "STALE_EVIDENCE"
    MISSING_SUPPORTING_EVIDENCE = (
        "MISSING_SUPPORTING_EVIDENCE"
    )


# ============================================================
# Data structures
# ============================================================


@dataclass(frozen=True)
class RiskStateReasonDetail:
    code: RiskStateReason
    severity: str
    message: str

    resource_type: Optional[str] = None
    resource_id: Optional[int] = None


@dataclass
class ContinuousRiskState:
    risk_id: int

    risk_state: RiskState
    treatment_state: TreatmentState

    reassessment_required: bool

    residual_risk_score: Optional[int]
    selected_treatment_id: Optional[int]

    reasons: list[RiskStateReasonDetail] = field(
        default_factory=list
    )

    @property
    def state(self) -> str:
        return self.risk_state.value

    @property
    def treatment_status(self) -> str:
        return self.treatment_state.value

    def as_dict(self) -> dict[str, Any]:
        return {
            "risk_id": self.risk_id,
            "risk_state": self.risk_state.value,
            "treatment_state": self.treatment_state.value,
            "reassessment_required": self.reassessment_required,
            "residual_risk_score": self.residual_risk_score,
            "selected_treatment_id": (
                self.selected_treatment_id
            ),
            "reasons": [
                {
                    "code": reason.code.value,
                    "severity": reason.severity,
                    "message": reason.message,
                    "resource_type": reason.resource_type,
                    "resource_id": reason.resource_id,
                }
                for reason in self.reasons
            ],
        }


# ============================================================
# Deterministic thresholds
# ============================================================


CRITICAL_RISK_SCORE = 20

LOW_CONTROL_EFFECTIVENESS_THRESHOLD = 50

STALE_EVIDENCE_DAYS = 90

OPEN_FINDING_STATUSES = {
    "Open",
    "In Progress",
    "Reopened",
}

OPEN_ACTION_STATUSES = {
    "Open",
    "In Progress",
    "Pending",
}

HIGH_FINDING_SEVERITIES = {
    "High",
    "Critical",
}

CRITICAL_FINDING_SEVERITY = "Critical"

CRITICAL_ACTION_PRIORITIES = {
    "Critical",
}


# ============================================================
# Normalisation helpers
# ============================================================


def _normalise(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip().lower()


def _utc_today() -> date:
    return datetime.now(timezone.utc).date()


def _as_date(value: Any) -> Optional[date]:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    return None


# ============================================================
# Finding helpers
# ============================================================


def _is_open_finding(
    finding: AuditFinding,
) -> bool:
    return (
        _normalise(finding.status)
        in {
            _normalise(status)
            for status in OPEN_FINDING_STATUSES
        }
    )


def _is_high_or_critical_finding(
    finding: AuditFinding,
) -> bool:
    return (
        _normalise(finding.severity)
        in {
            _normalise(severity)
            for severity in HIGH_FINDING_SEVERITIES
        }
    )


def _is_critical_finding(
    finding: AuditFinding,
) -> bool:
    return (
        _normalise(finding.severity)
        == _normalise(CRITICAL_FINDING_SEVERITY)
    )


# ============================================================
# Corrective action helpers
# ============================================================


def _is_open_action(
    action: CorrectiveAction,
) -> bool:
    return (
        _normalise(action.status)
        in {
            _normalise(status)
            for status in OPEN_ACTION_STATUSES
        }
    )


def _is_critical_action(
    action: CorrectiveAction,
) -> bool:
    return (
        _normalise(action.priority)
        in {
            _normalise(priority)
            for priority in CRITICAL_ACTION_PRIORITIES
        }
    )


def _is_overdue_action(
    action: CorrectiveAction,
    *,
    today: date,
) -> bool:
    if not _is_open_action(action):
        return False

    due_date = _as_date(
        getattr(action, "due_date", None)
    )

    if due_date is None:
        return False

    return due_date < today


# ============================================================
# Treatment helpers
# ============================================================


def _is_overdue_treatment(
    treatment: RiskTreatment,
    *,
    today: date,
) -> bool:
    status = _normalise(
        getattr(treatment, "status", None)
    )

    if status not in {
        "planned",
        "in progress",
    }:
        return False

    target_date = _as_date(
        getattr(treatment, "target_date", None)
    )

    if target_date is None:
        return False

    return target_date < today


# ============================================================
# Risk relationships
# ============================================================


def _get_risk_controls(
    risk: Risk,
    visible_user_ids: set[int] | None = None,
) -> list[Control]:
    controls: list[Control] = []

    for risk_control in (
        getattr(risk, "risk_controls", None) or []
    ):
        control = getattr(
            risk_control,
            "control",
            None,
        )

        if control is None:
            continue

        if (
            visible_user_ids is not None
            and control.owner_id not in visible_user_ids
        ):
            continue

        controls.append(control)

    return controls


def _get_risk_findings(
    db: Session,
    risk: Risk,
    visible_user_ids: set[int] | None = None,
) -> list[AuditFinding]:
    controls = _get_risk_controls(
        risk,
        visible_user_ids=None,
    )

    control_ids = [
        control.id
        for control in controls
        if getattr(control, "id", None) is not None
        and (
            visible_user_ids is None
            or control.owner_id in visible_user_ids
        )
    ]

    if not control_ids:
        return []

    query = (
        db.query(AuditFinding)
        .join(
            Audit,
            AuditFinding.audit_id == Audit.id,
        )
        .filter(
            AuditFinding.control_id.in_(control_ids)
        )
    )

    if visible_user_ids is not None:
        query = query.filter(
            Audit.auditor_id.in_(visible_user_ids)
        )

    return list(query.all())


def _get_risk_actions(
    db: Session,
    risk: Risk,
    visible_finding_user_ids: set[int] | None = None,
    visible_action_user_ids: set[int] | None = None,
) -> list[CorrectiveAction]:
    findings = _get_risk_findings(
        db,
        risk,
        visible_finding_user_ids,
    )

    finding_ids = [
        finding.id
        for finding in findings
        if getattr(finding, "id", None) is not None
    ]

    if not finding_ids:
        return []

    query = (
        db.query(CorrectiveAction)
        .filter(
            CorrectiveAction.finding_id.in_(
                finding_ids
            )
        )
    )

    if visible_action_user_ids is not None:
        query = query.filter(
            CorrectiveAction.assigned_to.in_(
                visible_action_user_ids
            )
        )

    return list(query.all())


def _get_risk_treatments(
    risk: Risk,
    visible_user_ids: set[int] | None = None,
) -> list[RiskTreatment]:
    treatments = list(
        getattr(
            risk,
            "risk_treatments",
            None,
        )
        or []
    )

    if visible_user_ids is None:
        return treatments

    return [
        treatment
        for treatment in treatments
        if treatment.owner_id in visible_user_ids
    ]


def _get_risk_evidence(
    db: Session,
    controls: Iterable[Control],
) -> list[Evidence]:
    control_ids = [
        control.id
        for control in controls
        if getattr(control, "id", None) is not None
    ]

    if not control_ids:
        return []

    return list(
        db.query(Evidence)
        .filter(
            Evidence.control_id.in_(control_ids)
        )
        .all()
    )


# ============================================================
# Evidence state
# ============================================================


def _is_stale_evidence(
    evidence: Evidence,
    *,
    today: date,
) -> bool:
    uploaded_at = getattr(
        evidence,
        "uploaded_at",
        None,
    )

    evidence_date = _as_date(uploaded_at)

    if evidence_date is None:
        return False

    stale_before = (
        today
        - timedelta(
            days=STALE_EVIDENCE_DAYS
        )
    )

    return evidence_date < stale_before


# ============================================================
# Treatment state
# ============================================================


def _calculate_treatment_state(
    treatment: Optional[RiskTreatment],
    *,
    findings: Iterable[AuditFinding],
    actions: Iterable[CorrectiveAction],
    today: date,
) -> tuple[
    TreatmentState,
    list[RiskStateReasonDetail],
]:
    if treatment is None:
        return (
            TreatmentState.REQUIRES_REASSESSMENT,
            [
                RiskStateReasonDetail(
                    code=(
                        RiskStateReason
                        .TREATMENT_MISSING_RESIDUAL
                    ),
                    severity="HIGH",
                    message=(
                        "No authoritative risk treatment "
                        "with a valid residual assessment "
                        "is available."
                    ),
                    resource_type="risk",
                )
            ],
        )

    reasons: list[
        RiskStateReasonDetail
    ] = []

    treatment_status = _normalise(
        getattr(
            treatment,
            "status",
            None,
        )
    )

    # --------------------------------------------------------
    # Cancelled treatment
    # --------------------------------------------------------

    if treatment_status == "cancelled":
        reasons.append(
            RiskStateReasonDetail(
                code=(
                    RiskStateReason
                    .TREATMENT_CANCELLED
                ),
                severity="HIGH",
                message=(
                    "The authoritative risk treatment "
                    "is cancelled."
                ),
                resource_type="risk_treatment",
                resource_id=treatment.id,
            )
        )

        return (
            TreatmentState.REQUIRES_REASSESSMENT,
            reasons,
        )

    # --------------------------------------------------------
    # Residual assessment
    # --------------------------------------------------------

    if not has_residual_assessment(
        treatment
    ):
        reasons.append(
            RiskStateReasonDetail(
                code=(
                    RiskStateReason
                    .TREATMENT_MISSING_RESIDUAL
                ),
                severity="HIGH",
                message=(
                    "The authoritative treatment does "
                    "not have a complete residual risk "
                    "assessment."
                ),
                resource_type="risk_treatment",
                resource_id=treatment.id,
            )
        )

        return (
            TreatmentState.REQUIRES_REASSESSMENT,
            reasons,
        )

    # --------------------------------------------------------
    # Findings
    # --------------------------------------------------------

    open_findings = [
        finding
        for finding in findings
        if _is_open_finding(finding)
        and _is_high_or_critical_finding(finding)
    ]

    critical_findings = [
        finding
        for finding in open_findings
        if _is_critical_finding(finding)
    ]

    if critical_findings:
        finding = critical_findings[0]

        reasons.append(
            RiskStateReasonDetail(
                code=(
                    RiskStateReason
                    .OPEN_CRITICAL_FINDING
                ),
                severity="CRITICAL",
                message=(
                    "An open critical finding is "
                    "associated with the risk."
                ),
                resource_type="audit_finding",
                resource_id=finding.id,
            )
        )

    elif open_findings:
        finding = open_findings[0]

        reasons.append(
            RiskStateReasonDetail(
                code=(
                    RiskStateReason
                    .OPEN_HIGH_FINDING
                ),
                severity="HIGH",
                message=(
                    "An open high-severity finding "
                    "is associated with the risk."
                ),
                resource_type="audit_finding",
                resource_id=finding.id,
            )
        )

    # --------------------------------------------------------
    # Corrective actions
    # --------------------------------------------------------

    overdue_actions = [
        action
        for action in actions
        if _is_overdue_action(
            action,
            today=today,
        )
    ]

    critical_open_actions = [
        action
        for action in actions
        if (
            _is_open_action(action)
            and _is_critical_action(action)
        )
    ]

    if overdue_actions:
        action = overdue_actions[0]

        reasons.append(
            RiskStateReasonDetail(
                code=(
                    RiskStateReason
                    .OVERDUE_CORRECTIVE_ACTION
                ),
                severity="HIGH",
                message=(
                    "An associated corrective action "
                    "is overdue."
                ),
                resource_type="corrective_action",
                resource_id=action.id,
            )
        )

    if critical_open_actions:
        action = critical_open_actions[0]

        reasons.append(
            RiskStateReasonDetail(
                code=(
                    RiskStateReason
                    .CRITICAL_CORRECTIVE_ACTION_OPEN
                ),
                severity="CRITICAL",
                message=(
                    "A critical corrective action "
                    "remains open."
                ),
                resource_type="corrective_action",
                resource_id=action.id,
            )
        )

    # --------------------------------------------------------
    # Treatment target date
    # --------------------------------------------------------

    if _is_overdue_treatment(
        treatment,
        today=today,
    ):
        reasons.append(
            RiskStateReasonDetail(
                code=(
                    RiskStateReason
                    .OVERDUE_TREATMENT
                ),
                severity="HIGH",
                message=(
                    "The authoritative risk treatment "
                    "has passed its target date."
                ),
                resource_type="risk_treatment",
                resource_id=treatment.id,
            )
        )

    # --------------------------------------------------------
    # State precedence
    # --------------------------------------------------------

    if any(
        reason.code
        in {
            RiskStateReason
            .OPEN_CRITICAL_FINDING,
            RiskStateReason
            .CRITICAL_CORRECTIVE_ACTION_OPEN,
        }
        for reason in reasons
    ):
        return (
            TreatmentState.REQUIRES_REASSESSMENT,
            reasons,
        )

    if reasons:
        return (
            TreatmentState.DEGRADED,
            reasons,
        )

    return (
        TreatmentState.CURRENT,
        [],
    )


# ============================================================
# Main state calculation
# ============================================================


def get_continuous_risk_state(
    db: Session,
    risk: Risk,
    *,
    current_user: User | None = None,
    today: Optional[date] = None,
) -> ContinuousRiskState:
    evaluation_date = (
        today
        if today is not None
        else _utc_today()
    )

    visible_control_users: set[int] | None = None
    visible_treatment_users: set[int] | None = None
    visible_finding_users: set[int] | None = None
    visible_action_users: set[int] | None = None

    if current_user is not None:
        visible_control_users = set(
            get_visible_user_ids(
                db,
                current_user,
                "controls",
            )
        )

        visible_treatment_users = set(
            get_visible_user_ids(
                db,
                current_user,
                "risk_treatments",
            )
        )

        visible_finding_users = set(
            get_visible_user_ids(
                db,
                current_user,
                "audit_findings",
            )
        )

        visible_action_users = set(
            get_visible_user_ids(
                db,
                current_user,
                "corrective_actions",
            )
        )

    controls = _get_risk_controls(
        risk,
        visible_control_users,
    )

    findings = _get_risk_findings(
        db,
        risk,
        visible_finding_users,
    )

    actions = _get_risk_actions(
        db,
        risk,
        visible_finding_user_ids=visible_finding_users,
        visible_action_user_ids=visible_action_users,
    )

    treatments = _get_risk_treatments(
        risk,
        visible_treatment_users,
    )

    evidence = _get_risk_evidence(
        db,
        controls,
    )

    # IMPORTANT:
    # Phase 55's canonical selector remains the only
    # authoritative treatment-selection mechanism.
    selected_treatment = (
        select_authoritative_treatment(
            treatments
        )
    )

    treatment_state, treatment_reasons = (
        _calculate_treatment_state(
            selected_treatment,
            findings=findings,
            actions=actions,
            today=evaluation_date,
        )
    )

    reasons = list(treatment_reasons)

    # ========================================================
    # Residual risk
    # ========================================================

    residual_risk_score: Optional[int] = None

    if selected_treatment is not None:
        residual_risk_score = getattr(
            selected_treatment,
            "residual_risk_score",
            None,
        )

    if (
        residual_risk_score is not None
        and residual_risk_score
        >= CRITICAL_RISK_SCORE
    ):
        reasons.append(
            RiskStateReasonDetail(
                code=(
                    RiskStateReason
                    .ELEVATED_RESIDUAL_RISK
                ),
                severity="CRITICAL",
                message=(
                    "The authoritative treatment residual "
                    "risk remains at or above the critical "
                    "threshold."
                ),
                resource_type="risk_treatment",
                resource_id=(
                    selected_treatment.id
                    if selected_treatment is not None
                    else None
                ),
            )
        )

    # ========================================================
    # Controls
    # ========================================================

    inactive_controls = [
        control
        for control in controls
        if _normalise(
            getattr(
                control,
                "status",
                None,
            )
        )
        != "active"
    ]

    low_effectiveness_controls = [
        control
        for control in controls
        if (
            getattr(
                control,
                "effectiveness",
                None,
            )
            is not None
            and control.effectiveness
            < LOW_CONTROL_EFFECTIVENESS_THRESHOLD
        )
    ]

    if inactive_controls:
        control = inactive_controls[0]

        reasons.append(
            RiskStateReasonDetail(
                code=(
                    RiskStateReason
                    .CONTROL_INACTIVE
                ),
                severity="HIGH",
                message=(
                    "A control supporting the risk "
                    "is not active."
                ),
                resource_type="control",
                resource_id=control.id,
            )
        )

    if low_effectiveness_controls:
        control = low_effectiveness_controls[0]

        reasons.append(
            RiskStateReasonDetail(
                code=(
                    RiskStateReason
                    .CONTROL_EFFECTIVENESS_LOW
                ),
                severity="HIGH",
                message=(
                    "A supporting control has effectiveness "
                    f"below {LOW_CONTROL_EFFECTIVENESS_THRESHOLD}%."
                ),
                resource_type="control",
                resource_id=control.id,
            )
        )

    # ========================================================
    # Evidence
    # ========================================================

    if controls and not evidence:
        reasons.append(
            RiskStateReasonDetail(
                code=(
                    RiskStateReason
                    .MISSING_SUPPORTING_EVIDENCE
                ),
                severity="HIGH",
                message=(
                    "No supporting evidence is currently "
                    "associated with the controls supporting "
                    "this risk."
                ),
                resource_type="risk",
                resource_id=risk.id,
            )
        )

    stale_evidence = [
        item
        for item in evidence
        if _is_stale_evidence(
            item,
            today=evaluation_date,
        )
    ]

    if stale_evidence:
        item = stale_evidence[0]

        reasons.append(
            RiskStateReasonDetail(
                code=(
                    RiskStateReason
                    .STALE_EVIDENCE
                ),
                severity="HIGH",
                message=(
                    "Supporting evidence is older than "
                    f"{STALE_EVIDENCE_DAYS} days."
                ),
                resource_type="evidence",
                resource_id=item.id,
            )
        )

    # ========================================================
    # Final risk-state precedence
    # ========================================================

    if (
        treatment_state
        == TreatmentState.REQUIRES_REASSESSMENT
    ):
        risk_state = (
            RiskState.REASSESSMENT_REQUIRED
        )

    elif any(
        reason.code
        in {
            RiskStateReason.OPEN_CRITICAL_FINDING,
            RiskStateReason.CRITICAL_CORRECTIVE_ACTION_OPEN,
        }
        for reason in reasons
    ):
        risk_state = RiskState.REASSESSMENT_REQUIRED

    elif reasons:
        risk_state = RiskState.DEGRADED

    else:
        risk_state = RiskState.CURRENT

    reassessment_required = (
        risk_state
        == RiskState.REASSESSMENT_REQUIRED
    )

    return ContinuousRiskState(
        risk_id=risk.id,
        risk_state=risk_state,
        treatment_state=treatment_state,
        reassessment_required=(
            reassessment_required
        ),
        residual_risk_score=(
            residual_risk_score
        ),
        selected_treatment_id=(
            selected_treatment.id
            if selected_treatment is not None
            else None
        ),
        reasons=reasons,
    )


# ============================================================
# ID-based helper
# ============================================================


def get_continuous_risk_state_by_id(
    db: Session,
    risk_id: int,
    *,
    today: Optional[date] = None,
) -> Optional[ContinuousRiskState]:
    risk = (
        db.query(Risk)
        .filter(
            Risk.id == risk_id
        )
        .first()
    )

    if risk is None:
        return None

    return get_continuous_risk_state(
        db,
        risk,
        today=today,
    )