from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.control import Control
from app.models.corrective_action import CorrectiveAction
from app.models.evidence import Evidence
from app.models.framework import Framework
from app.models.risk import Risk
from app.models.risk_treatment import RiskTreatment
from app.models.risk_response_workflow import (
    RiskResponseWorkflowRecord,
)


CRITICAL_RISK_SCORE = 20
HIGH_RISK_SCORE = 15

INEFFECTIVE_CONTROL_THRESHOLD = 50
DEGRADED_CONTROL_THRESHOLD = 70

STALE_EVIDENCE_DAYS = 90

OPEN_FINDING_STATUSES = {
    "open",
    "in progress",
    "pending",
}

CRITICAL_FINDING_SEVERITIES = {
    "critical",
}

OPEN_ACTION_STATUSES = {
    "pending",
    "open",
    "in progress",
}

ACTIVE_TREATMENT_STATUSES = {
    "planned",
    "in progress",
}

OPEN_WORKFLOW_STATUSES = {
    "PENDING",
    "IN_PROGRESS",
    "BLOCKED",
    "ESCALATED",
}


def _normalise(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip().lower()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _today() -> date:
    return _utcnow().date()


def _as_date(value: Any) -> date | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    return None


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


def _is_critical_finding(
    finding: AuditFinding,
) -> bool:
    return (
        _normalise(finding.severity)
        in {
            _normalise(severity)
            for severity in CRITICAL_FINDING_SEVERITIES
        }
    )


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


def _is_overdue_action(
    action: CorrectiveAction,
) -> bool:
    if not _is_open_action(action):
        return False

    due_date = _as_date(
        getattr(action, "due_date", None)
    )

    if due_date is None:
        return False

    return due_date < _today()


def _is_overdue_treatment(
    treatment: RiskTreatment,
) -> bool:
    if (
        _normalise(treatment.status)
        not in {
            _normalise(status)
            for status in ACTIVE_TREATMENT_STATUSES
        }
    ):
        return False

    target_date = _as_date(
        getattr(treatment, "target_date", None)
    )

    if target_date is None:
        return False

    return target_date < _today()


def _is_stale_evidence(
    evidence: Evidence,
) -> bool:
    uploaded_at = getattr(
        evidence,
        "uploaded_at",
        None,
    )

    if uploaded_at is None:
        return True

    if uploaded_at.tzinfo is None:
        uploaded_at = uploaded_at.replace(
            tzinfo=timezone.utc
        )

    age_days = (
        _utcnow() - uploaded_at
    ).days

    return age_days >= STALE_EVIDENCE_DAYS


def _risk_posture(
    risks: list[Risk],
) -> str:
    if not risks:
        return "NO_DATA"

    critical = sum(
        risk.risk_score >= CRITICAL_RISK_SCORE
        for risk in risks
    )

    high = sum(
        HIGH_RISK_SCORE
        <= risk.risk_score
        < CRITICAL_RISK_SCORE
        for risk in risks
    )

    if critical > 0:
        return "CRITICAL"

    if high > 0:
        return "HIGH"

    average = (
        sum(
            risk.risk_score
            for risk in risks
        )
        / len(risks)
    )

    if average >= 10:
        return "MODERATE"

    return "LOW"


def _compliance_posture(
    controls: list[Control],
) -> str:
    active_controls = [
        control
        for control in controls
        if _normalise(
            control.status
        )
        == "active"
    ]

    if not active_controls:
        return "NO_DATA"

    average = sum(
        float(
            control.effectiveness or 0
        )
        for control in active_controls
    ) / len(active_controls)

    if average >= 80:
        return "STRONG"

    if average >= 70:
        return "MODERATE"

    if average >= 50:
        return "WEAK"

    return "CRITICAL"


def _control_health(
    controls: list[Control],
) -> dict[str, Any]:
    active = [
        control
        for control in controls
        if _normalise(
            control.status
        )
        == "active"
    ]

    ineffective = [
        control
        for control in active
        if (
            control.effectiveness is not None
            and control.effectiveness
            < INEFFECTIVE_CONTROL_THRESHOLD
        )
    ]

    degraded = [
        control
        for control in active
        if (
            control.effectiveness is not None
            and (
                DEGRADED_CONTROL_THRESHOLD
                > control.effectiveness
                >= INEFFECTIVE_CONTROL_THRESHOLD
            )
        )
    ]

    healthy = [
        control
        for control in active
        if (
            control.effectiveness is not None
            and control.effectiveness
            >= DEGRADED_CONTROL_THRESHOLD
        )
    ]

    average = (
        sum(
            float(
                control.effectiveness or 0
            )
            for control in active
        )
        / len(active)
        if active
        else 0.0
    )

    return {
        "total": len(controls),
        "active": len(active),
        "healthy": len(healthy),
        "degraded": len(degraded),
        "ineffective": len(ineffective),
        "average_effectiveness": round(
            average,
            2,
        ),
    }


def _risk_trends(
    risks: list[Risk],
) -> dict[str, int]:
    """
    Provide a deterministic distribution of the
    current risk population.

    This intentionally avoids inventing historical
    trend data when no risk-history table exists.
    """

    return {
        "critical": sum(
            risk.risk_score
            >= CRITICAL_RISK_SCORE
            for risk in risks
        ),
        "high": sum(
            HIGH_RISK_SCORE
            <= risk.risk_score
            < CRITICAL_RISK_SCORE
            for risk in risks
        ),
        "moderate": sum(
            8 <= risk.risk_score < HIGH_RISK_SCORE
            for risk in risks
        ),
        "low": sum(
            risk.risk_score < 8
            for risk in risks
        ),
    }


def _regulatory_exposure(
    db: Session,
    controls: list[Control],
) -> dict[str, Any]:
    control_ids = {
        control.id
        for control in controls
    }

    frameworks: dict[str, dict[str, Any]] = {}

    all_frameworks = db.query(
        Framework
    ).all()

    for framework in all_frameworks:
        mapped_controls = 0

        for framework_control in getattr(
            framework,
            "framework_controls",
            None,
        ) or []:
            for mapping in getattr(
                framework_control,
                "control_mappings",
                None,
            ) or []:
                control = getattr(
                    mapping,
                    "control",
                    None,
                )

                if (
                    control is not None
                    and control.id in control_ids
                ):
                    mapped_controls += 1

        frameworks[
            framework.name
        ] = {
            "control_count": mapped_controls,
            "exposure": (
                "ELEVATED"
                if mapped_controls == 0
                else "MONITORED"
            ),
        }

    return {
        "framework_count": len(frameworks),
        "frameworks": frameworks,
    }


def _business_unit_exposure(
    db: Session,
    risks: list[Risk],
) -> list[dict[str, Any]]:
    """
    Users represent the current organizational ownership
    boundary in the existing model. Aggregate risk exposure
    by owner rather than inventing a separate business-unit
    model.
    """

    counts: dict[int, dict[str, Any]] = {}

    for risk in risks:
        owner = getattr(
            risk,
            "owner",
            None,
        )

        owner_id = risk.owner_id

        if owner_id not in counts:
            counts[owner_id] = {
                "owner_id": owner_id,
                "owner_name": (
                    getattr(
                        owner,
                        "full_name",
                        None,
                    )
                    or f"User {owner_id}"
                ),
                "risk_count": 0,
                "critical_risks": 0,
                "high_risks": 0,
                "max_risk_score": 0,
            }

        item = counts[owner_id]

        item["risk_count"] += 1

        if (
            risk.risk_score
            >= CRITICAL_RISK_SCORE
        ):
            item["critical_risks"] += 1

        elif (
            risk.risk_score
            >= HIGH_RISK_SCORE
        ):
            item["high_risks"] += 1

        item["max_risk_score"] = max(
            item["max_risk_score"],
            risk.risk_score,
        )

    return sorted(
        counts.values(),
        key=lambda item: (
            -item["critical_risks"],
            -item["high_risks"],
            -item["max_risk_score"],
        ),
    )


def _build_explainability(
    risks: list[Risk],
    controls: list[Control],
    findings: list[AuditFinding],
    actions: list[CorrectiveAction],
    treatments: list[RiskTreatment],
) -> list[dict[str, Any]]:
    explanations: list[dict[str, Any]] = []

    critical_risks = [
        risk
        for risk in risks
        if risk.risk_score
        >= CRITICAL_RISK_SCORE
    ]

    ineffective_controls = [
        control
        for control in controls
        if (
            control.effectiveness is not None
            and control.effectiveness
            < INEFFECTIVE_CONTROL_THRESHOLD
        )
    ]

    overdue_actions = [
        action
        for action in actions
        if _is_overdue_action(action)
    ]

    overdue_treatments = [
        treatment
        for treatment in treatments
        if _is_overdue_treatment(treatment)
    ]

    open_critical_findings = [
        finding
        for finding in findings
        if (
            _is_open_finding(finding)
            and _is_critical_finding(finding)
        )
    ]

    if critical_risks:
        explanations.append(
            {
                "signal": "CRITICAL_RISKS",
                "severity": "CRITICAL",
                "count": len(
                    critical_risks
                ),
                "why": (
                    "Critical risk scores are "
                    "driving the current enterprise "
                    "risk posture."
                ),
            }
        )

    if ineffective_controls:
        explanations.append(
            {
                "signal": "INEFFECTIVE_CONTROLS",
                "severity": "HIGH",
                "count": len(
                    ineffective_controls
                ),
                "why": (
                    "Controls below the effectiveness "
                    "threshold reduce the strength of "
                    "the current compliance posture."
                ),
            }
        )

    if open_critical_findings:
        explanations.append(
            {
                "signal": "CRITICAL_FINDINGS",
                "severity": "CRITICAL",
                "count": len(
                    open_critical_findings
                ),
                "why": (
                    "Open critical findings represent "
                    "unresolved assurance exposure."
                ),
            }
        )

    if overdue_actions:
        explanations.append(
            {
                "signal": "OVERDUE_CORRECTIVE_ACTIONS",
                "severity": "HIGH",
                "count": len(
                    overdue_actions
                ),
                "why": (
                    "Overdue corrective actions indicate "
                    "remediation is not progressing within "
                    "its expected timeline."
                ),
            }
        )

    if overdue_treatments:
        explanations.append(
            {
                "signal": "OVERDUE_TREATMENTS",
                "severity": "HIGH",
                "count": len(
                    overdue_treatments
                ),
                "why": (
                    "Overdue risk treatments can weaken "
                    "the reliability of current risk "
                    "response assumptions."
                ),
            }
        )

    if not explanations:
        explanations.append(
            {
                "signal": "NO_MAJOR_EXPOSURE",
                "severity": "LOW",
                "count": 0,
                "why": (
                    "No major deterministic executive "
                    "exposure signal was detected in the "
                    "visible GRC data."
                ),
            }
        )

    return explanations


def build_executive_intelligence(
    db: Session,
    visible_user_ids: list[int],
) -> dict[str, Any]:
    """
    Build deterministic, read-only executive GRC intelligence.

    All primary resource populations are constrained to the
    caller's visibility boundary.

    No database writes occur.
    """

    visible_ids = set(
        visible_user_ids
    )

    risks = list(
        db.query(Risk)
        .filter(
            Risk.owner_id.in_(visible_ids)
        )
        .all()
    )

    controls = list(
        db.query(Control)
        .filter(
            Control.owner_id.in_(visible_ids)
        )
        .all()
    )

    evidence = list(
        db.query(Evidence)
        .filter(
            Evidence.uploaded_by.in_(
                visible_ids
            )
        )
        .all()
    )

    audits = list(
        db.query(Audit)
        .filter(
            Audit.auditor_id.in_(visible_ids)
        )
        .all()
    )

    audit_ids = {
        audit.id
        for audit in audits
    }

    findings = list(
        db.query(AuditFinding)
        .filter(
            AuditFinding.audit_id.in_(
                audit_ids
            )
        )
        .all()
    ) if audit_ids else []

    finding_ids = {
        finding.id
        for finding in findings
    }

    actions = list(
        db.query(CorrectiveAction)
        .filter(
            CorrectiveAction.finding_id.in_(
                finding_ids
            )
        )
        .all()
    ) if finding_ids else []

    treatments = list(
        db.query(RiskTreatment)
        .filter(
            RiskTreatment.owner_id.in_(
                visible_ids
            )
        )
        .all()
    )

    risk_ids = {
        risk.id
        for risk in risks
    }

    workflows = list(
        db.query(
            RiskResponseWorkflowRecord
        )
        .filter(
            RiskResponseWorkflowRecord.risk_id.in_(
                risk_ids
            )
        )
        .all()
    ) if risk_ids else []

    open_findings = [
        finding
        for finding in findings
        if _is_open_finding(finding)
    ]

    critical_findings = [
        finding
        for finding in open_findings
        if _is_critical_finding(finding)
    ]

    open_actions = [
        action
        for action in actions
        if _is_open_action(action)
    ]

    overdue_actions = [
        action
        for action in open_actions
        if _is_overdue_action(action)
    ]

    overdue_treatments = [
        treatment
        for treatment in treatments
        if _is_overdue_treatment(treatment)
    ]

    stale_evidence = [
        item
        for item in evidence
        if _is_stale_evidence(item)
    ]

    critical_risks = [
        risk
        for risk in risks
        if risk.risk_score
        >= CRITICAL_RISK_SCORE
    ]

    high_risks = [
        risk
        for risk in risks
        if (
            HIGH_RISK_SCORE
            <= risk.risk_score
            < CRITICAL_RISK_SCORE
        )
    ]

    open_workflows = [
        workflow
        for workflow in workflows
        if _normalise(
            workflow.status
        ).upper()
        in OPEN_WORKFLOW_STATUSES
    ]

    workflow_health = {
        "total": len(workflows),
        "open": len(open_workflows),
        "completed": sum(
            _normalise(
                workflow.status
            ).upper()
            == "COMPLETED"
            for workflow in workflows
        ),
        "blocked": sum(
            _normalise(
                workflow.status
            ).upper()
            == "BLOCKED"
            for workflow in workflows
        ),
        "escalated": sum(
            _normalise(
                workflow.status
            ).upper()
            == "ESCALATED"
            for workflow in workflows
        ),
    }

    control_health = _control_health(
        controls
    )

    active_controls = [
        control
        for control in controls
        if _normalise(
            control.status
        )
        == "active"
    ]

    evidence_control_ids = {
        evidence_item.control_id
        for evidence_item in evidence
    }

    controls_without_evidence = [
        control
        for control in active_controls
        if control.id
        not in evidence_control_ids
    ]

    compliance_score = round(
        control_health[
            "average_effectiveness"
        ],
        2,
    )

    return {
        "risk_posture": {
            "level": _risk_posture(risks),
            "total": len(risks),
            "critical": len(
                critical_risks
            ),
            "high": len(high_risks),
            "average_score": round(
                (
                    sum(
                        risk.risk_score
                        for risk in risks
                    )
                    / len(risks)
                    if risks
                    else 0.0
                ),
                2,
            ),
            "distribution": _risk_trends(
                risks
            ),
        },
        "compliance_posture": {
            "level": _compliance_posture(
                controls
            ),
            "score": compliance_score,
            "active_controls": len(
                active_controls
            ),
            "controls_without_evidence": len(
                controls_without_evidence
            ),
            "stale_evidence": len(
                stale_evidence
            ),
        },
        "control_health": control_health,
        "regulatory_exposure":
            _regulatory_exposure(
                db,
                controls,
            ),
        "findings": {
            "total": len(findings),
            "open": len(open_findings),
            "critical_open": len(
                critical_findings
            ),
        },
        "remediation": {
            "total_actions": len(actions),
            "open_actions": len(
                open_actions
            ),
            "overdue_actions": len(
                overdue_actions
            ),
        },
        "treatment_effectiveness": {
            "total": len(treatments),
            "active": sum(
                _normalise(
                    treatment.status
                )
                in {
                    _normalise(status)
                    for status in ACTIVE_TREATMENT_STATUSES
                }
                for treatment in treatments
            ),
            "overdue": len(
                overdue_treatments
            ),
            "with_residual_risk": sum(
                treatment.residual_risk_score
                is not None
                for treatment in treatments
            ),
            "elevated_residual_risk": sum(
                (
                    treatment.residual_risk_score
                    is not None
                    and treatment.residual_risk_score
                    >= HIGH_RISK_SCORE
                )
                for treatment in treatments
            ),
        },
        "workflow_health": workflow_health,
        "regulatory": _regulatory_exposure(
            db,
            controls,
        ),
        "business_unit_exposure":
            _business_unit_exposure(
                db,
                risks,
            ),
        "explainability":
            _build_explainability(
                risks,
                controls,
                findings,
                actions,
                treatments,
            ),
        "scope": {
            "visible_user_count":
                len(visible_ids),
            "risk_count": len(risks),
            "control_count": len(controls),
            "evidence_count": len(evidence),
        },
        "generated_at":
            _utcnow().isoformat(),
    }