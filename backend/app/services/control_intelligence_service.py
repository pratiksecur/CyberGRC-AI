from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.control import Control
from app.models.control_framework_control import (
    ControlFrameworkControl,
)
from app.models.corrective_action import CorrectiveAction
from app.models.evidence import Evidence
from app.models.framework import Framework
from app.models.framework_control import FrameworkControl
from app.models.risk import Risk
from app.models.risk_control import RiskControl


# ==========================================================
# PHASE 63 — CONTROL INTELLIGENCE
# ==========================================================

INEFFECTIVE_CONTROL_THRESHOLD = 50
DEGRADED_EFFECTIVENESS_THRESHOLD = 70
HEALTHY_EFFECTIVENESS_THRESHOLD = 80

EVIDENCE_AGING_DAYS = 30
EVIDENCE_STALE_DAYS = 90

HIGH_RISK_SCORE = 15
CRITICAL_RISK_SCORE = 20


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value


def _age_days(
    uploaded_at: datetime | None,
    now: datetime,
) -> int | None:

    uploaded_at = _ensure_aware(uploaded_at)

    if uploaded_at is None:
        return None

    delta = now - uploaded_at

    return max(
        0,
        delta.days,
    )


def _evidence_state(
    evidence: list[Evidence],
    now: datetime,
) -> dict[str, Any]:

    if not evidence:
        return {
            "count": 0,
            "fresh": 0,
            "aging": 0,
            "stale": 0,
            "freshness_score": 0,
            "state": "MISSING",
        }

    fresh = 0
    aging = 0
    stale = 0
    scores: list[float] = []

    for item in evidence:

        age = _age_days(
            item.uploaded_at,
            now,
        )

        if age is None:
            stale += 1
            scores.append(0)
            continue

        if age <= EVIDENCE_AGING_DAYS:

            fresh += 1

            score = 100

        elif age <= EVIDENCE_STALE_DAYS:

            aging += 1

            span = (
                EVIDENCE_STALE_DAYS
                - EVIDENCE_AGING_DAYS
            )

            score = max(
                50,
                100
                - (
                    (
                        age
                        - EVIDENCE_AGING_DAYS
                    )
                    / span
                    * 50
                ),
            )

        else:

            stale += 1

            score = max(
                0,
                50
                - (
                    (
                        age
                        - EVIDENCE_STALE_DAYS
                    )
                    / EVIDENCE_STALE_DAYS
                    * 50
                ),
            )

        scores.append(float(score))

    average_score = (
        sum(scores) / len(scores)
        if scores
        else 0
    )

    if stale == len(evidence):

        state = "STALE"

    elif stale > 0:

        state = "MIXED"

    elif aging > 0:

        state = "AGING"

    else:

        state = "FRESH"

    return {
        "count": len(evidence),
        "fresh": fresh,
        "aging": aging,
        "stale": stale,
        "freshness_score": round(
            average_score,
            1,
        ),
        "state": state,
    }


def _get_risks(
    db: Session,
    control_id: int,
    visible_user_ids: set[int],
) -> list[Risk]:

    return (
        db.query(Risk)
        .join(
            RiskControl,
            RiskControl.risk_id == Risk.id,
        )
        .filter(
            RiskControl.control_id == control_id,
            Risk.owner_id.in_(
                visible_user_ids
            ),
        )
        .order_by(
            Risk.risk_score.desc(),
            Risk.id.asc(),
        )
        .all()
    )


def _get_framework_names(
    db: Session,
    control_id: int,
) -> list[str]:

    rows = (
        db.query(Framework.name)
        .join(
            FrameworkControl,
            FrameworkControl.framework_id
            == Framework.id,
        )
        .join(
            ControlFrameworkControl,
            ControlFrameworkControl.framework_control_id
            == FrameworkControl.id,
        )
        .filter(
            ControlFrameworkControl.control_id
            == control_id
        )
        .distinct()
        .order_by(
            Framework.name.asc()
        )
        .all()
    )

    return [
        row[0]
        for row in rows
    ]


def _get_findings(
    db: Session,
    control_id: int,
    visible_user_ids: set[int],
) -> list[AuditFinding]:

    return (
        db.query(AuditFinding)
        .join(
            Audit,
            Audit.id == AuditFinding.audit_id,
        )
        .filter(
            AuditFinding.control_id
            == control_id,
            Audit.auditor_id.in_(
                visible_user_ids
            ),
        )
        .order_by(
            AuditFinding.id.asc()
        )
        .all()
    )


def _get_corrective_actions(
    db: Session,
    findings: list[AuditFinding],
    visible_user_ids: set[int],
) -> list[CorrectiveAction]:

    if not findings:
        return []

    finding_ids = {
        finding.id
        for finding in findings
    }

    return (
        db.query(CorrectiveAction)
        .filter(
            CorrectiveAction.finding_id.in_(
                finding_ids
            ),
            CorrectiveAction.assigned_to.in_(
                visible_user_ids
            ),
        )
        .order_by(
            CorrectiveAction.id.asc()
        )
        .all()
    )


def _is_open_finding(
    finding: AuditFinding,
) -> bool:

    status = (
        str(finding.status or "")
        .strip()
        .lower()
    )

    return status not in {
        "closed",
        "resolved",
        "completed",
    }


def _is_open_action(
    action: CorrectiveAction,
) -> bool:

    status = (
        str(action.status or "")
        .strip()
        .lower()
    )

    return status not in {
        "closed",
        "completed",
        "resolved",
    }


def _calculate_health_score(
    effectiveness: int,
    evidence_score: float,
    evidence_exists: bool,
    risk_count: int,
    high_risk_count: int,
    critical_finding_count: int,
    open_finding_count: int,
    active: bool,
) -> float:

    # ------------------------------------------------------
    # Base score
    # ------------------------------------------------------

    score = (
        effectiveness * 0.55
        + evidence_score * 0.25
        + (
            10
            if evidence_exists
            else 0
        )
        + (
            10
            if risk_count > 0
            else 0
        )
    )

    # ------------------------------------------------------
    # Exposure penalties
    # ------------------------------------------------------

    score -= min(
        15,
        high_risk_count * 5,
    )

    score -= min(
        25,
        critical_finding_count * 15,
    )

    score -= min(
        15,
        max(
            0,
            open_finding_count
            - critical_finding_count,
        )
        * 5,
    )

    if not active:
        score -= 15

    return round(
        max(
            0,
            min(
                100,
                score,
            ),
        ),
        1,
    )


def _health_state(
    health_score: float,
    effectiveness: int,
    evidence_exists: bool,
    stale_evidence: int,
    critical_findings: int,
) -> str:

    if (
        critical_findings > 0
        or effectiveness
        <= INEFFECTIVE_CONTROL_THRESHOLD
        or health_score < 50
    ):
        return "CRITICAL"

    if (
        not evidence_exists
        or stale_evidence > 0
        or effectiveness
        < DEGRADED_EFFECTIVENESS_THRESHOLD
        or health_score < 75
    ):
        return "DEGRADED"

    return "HEALTHY"


def _trend_signal(
    effectiveness: int,
    evidence_state: str,
    stale_evidence: int,
    high_risk_count: int,
    critical_findings: int,
    open_findings: int,
) -> str:

    if (
        critical_findings > 0
        or effectiveness
        <= INEFFECTIVE_CONTROL_THRESHOLD
        or stale_evidence > 0
    ):
        return "DEGRADING"

    if (
        effectiveness
        < DEGRADED_EFFECTIVENESS_THRESHOLD
        or evidence_state
        in {
            "AGING",
            "MIXED",
        }
        or high_risk_count > 0
        or open_findings > 0
    ):
        return "WATCH"

    return "STABLE"


def _monitoring_signals(
    control: Control,
    evidence_state: dict[str, Any],
    risks: list[Risk],
    findings: list[AuditFinding],
    actions: list[CorrectiveAction],
) -> list[str]:

    signals: list[str] = []

    if control.status != "Active":
        signals.append(
            "CONTROL_INACTIVE"
        )

    if not evidence_state["count"]:
        signals.append(
            "MISSING_EVIDENCE"
        )

    if evidence_state["stale"] > 0:
        signals.append(
            "STALE_EVIDENCE"
        )

    if (
        control.effectiveness
        <= INEFFECTIVE_CONTROL_THRESHOLD
    ):
        signals.append(
            "LOW_EFFECTIVENESS"
        )

    if any(
        risk.risk_score
        >= CRITICAL_RISK_SCORE
        for risk in risks
    ):
        signals.append(
            "CRITICAL_RISK_EXPOSURE"
        )

    elif any(
        risk.risk_score
        >= HIGH_RISK_SCORE
        for risk in risks
    ):
        signals.append(
            "HIGH_RISK_EXPOSURE"
        )

    if any(
        _is_open_finding(finding)
        for finding in findings
    ):
        signals.append(
            "OPEN_CONTROL_FINDING"
        )

    if any(
        str(
            finding.severity or ""
        ).lower()
        == "critical"
        and _is_open_finding(finding)
        for finding in findings
    ):
        signals.append(
            "CRITICAL_CONTROL_FINDING"
        )

    today = _utc_now().date()

    if any(
        _is_open_action(action)
        and action.due_date
        and action.due_date < today
        for action in actions
    ):
        signals.append(
            "OVERDUE_REMEDIATION"
        )

    return signals


def get_control_intelligence(
    db: Session,
    control: Control,
    visible_user_ids: set[int],
    now: datetime | None = None,
) -> dict[str, Any]:

    now = now or _utc_now()

    visible_user_ids = set(
        visible_user_ids
    )

    # ------------------------------------------------------
    # Evidence
    # ------------------------------------------------------

    evidence = (
        db.query(Evidence)
        .filter(
            Evidence.control_id
            == control.id,
            Evidence.uploaded_by.in_(
                visible_user_ids
            ),
        )
        .order_by(
            Evidence.id.asc()
        )
        .all()
    )

    evidence_state = _evidence_state(
        evidence,
        now,
    )

    # ------------------------------------------------------
    # Risks
    # ------------------------------------------------------

    risks = _get_risks(
        db,
        control.id,
        visible_user_ids,
    )

    high_risk_count = sum(
        1
        for risk in risks
        if risk.risk_score
        >= HIGH_RISK_SCORE
    )

    critical_risk_count = sum(
        1
        for risk in risks
        if risk.risk_score
        >= CRITICAL_RISK_SCORE
    )

    # ------------------------------------------------------
    # Frameworks
    # ------------------------------------------------------

    framework_names = _get_framework_names(
        db,
        control.id,
    )

    # ------------------------------------------------------
    # Findings / remediation
    # ------------------------------------------------------

    findings = _get_findings(
        db,
        control.id,
        visible_user_ids,
    )

    open_findings = [
        finding
        for finding in findings
        if _is_open_finding(finding)
    ]

    critical_findings = [
        finding
        for finding in open_findings
        if str(
            finding.severity or ""
        ).lower()
        == "critical"
    ]

    corrective_actions = (
        _get_corrective_actions(
            db,
            findings,
            visible_user_ids,
        )
    )

    open_actions = [
        action
        for action in corrective_actions
        if _is_open_action(action)
    ]

    overdue_actions = [
        action
        for action in open_actions
        if (
            action.due_date
            and action.due_date
            < now.date()
        )
    ]

    # ------------------------------------------------------
    # Health
    # ------------------------------------------------------

    health_score = _calculate_health_score(
        effectiveness=control.effectiveness,
        evidence_score=evidence_state[
            "freshness_score"
        ],
        evidence_exists=bool(evidence),
        risk_count=len(risks),
        high_risk_count=high_risk_count,
        critical_finding_count=len(
            critical_findings
        ),
        open_finding_count=len(
            open_findings
        ),
        active=control.status == "Active",
    )

    health_state = _health_state(
        health_score=health_score,
        effectiveness=control.effectiveness,
        evidence_exists=bool(evidence),
        stale_evidence=evidence_state[
            "stale"
        ],
        critical_findings=len(
            critical_findings
        ),
    )

    trend_signal = _trend_signal(
        effectiveness=control.effectiveness,
        evidence_state=evidence_state[
            "state"
        ],
        stale_evidence=evidence_state[
            "stale"
        ],
        high_risk_count=high_risk_count,
        critical_findings=len(
            critical_findings
        ),
        open_findings=len(
            open_findings
        ),
    )

    monitoring_signals = _monitoring_signals(
        control,
        evidence_state,
        risks,
        findings,
        corrective_actions,
    )

    remediation_required = bool(
        monitoring_signals
    )

    # ------------------------------------------------------
    # Recommended action
    # ------------------------------------------------------

    if (
        "CRITICAL_CONTROL_FINDING"
        in monitoring_signals
    ):
        recommended_action = (
            "Immediately review the critical "
            "control finding and initiate "
            "remediation."
        )

    elif (
        "LOW_EFFECTIVENESS"
        in monitoring_signals
    ):
        recommended_action = (
            "Review control design and "
            "operating effectiveness."
        )

    elif (
        "MISSING_EVIDENCE"
        in monitoring_signals
    ):
        recommended_action = (
            "Collect and attach current "
            "supporting evidence."
        )

    elif (
        "STALE_EVIDENCE"
        in monitoring_signals
    ):
        recommended_action = (
            "Refresh stale control evidence."
        )

    elif (
        "OVERDUE_REMEDIATION"
        in monitoring_signals
    ):
        recommended_action = (
            "Review overdue corrective "
            "actions and update remediation."
        )

    elif (
        "HIGH_RISK_EXPOSURE"
        in monitoring_signals
        or "CRITICAL_RISK_EXPOSURE"
        in monitoring_signals
    ):
        recommended_action = (
            "Review the control against "
            "associated risk exposure."
        )

    else:
        recommended_action = (
            "Continue continuous monitoring."
        )

    return {
        "control_id": control.id,
        "title": control.title,
        "control_type": control.control_type,
        "status": control.status,
        "effectiveness": control.effectiveness,
        "health_score": health_score,
        "health_state": health_state,
        "effectiveness_trend_signal": trend_signal,
        "evidence_count": evidence_state[
            "count"
        ],
        "fresh_evidence": evidence_state[
            "fresh"
        ],
        "aging_evidence": evidence_state[
            "aging"
        ],
        "stale_evidence": evidence_state[
            "stale"
        ],
        "evidence_freshness_score": evidence_state[
            "freshness_score"
        ],
        "evidence_state": evidence_state[
            "state"
        ],
        "risk_count": len(risks),
        "high_risk_count": high_risk_count,
        "critical_risk_count": critical_risk_count,
        "risk_ids": [
            risk.id
            for risk in risks
        ],
        "risk_titles": [
            risk.title
            for risk in risks
        ],
        "framework_count": len(
            framework_names
        ),
        "framework_names": framework_names,
        "open_finding_count": len(
            open_findings
        ),
        "critical_finding_count": len(
            critical_findings
        ),
        "open_corrective_action_count": len(
            open_actions
        ),
        "overdue_corrective_action_count": len(
            overdue_actions
        ),
        "monitoring_signals": monitoring_signals,
        "remediation_required": remediation_required,
        "recommended_action": recommended_action,
    }


def build_control_intelligence_report(
    db: Session,
    visible_user_ids: list[int] | set[int],
    now: datetime | None = None,
) -> dict[str, Any]:

    now = now or _utc_now()

    visible_user_ids = set(
        visible_user_ids
    )

    controls = (
        db.query(Control)
        .filter(
            Control.owner_id.in_(
                visible_user_ids
            )
        )
        .order_by(
            Control.id.asc()
        )
        .all()
    )

    items = [
        get_control_intelligence(
            db,
            control,
            visible_user_ids,
            now,
        )
        for control in controls
    ]

    total_controls = len(items)

    healthy_controls = sum(
        1
        for item in items
        if item["health_state"]
        == "HEALTHY"
    )

    degraded_controls = sum(
        1
        for item in items
        if item["health_state"]
        == "DEGRADED"
    )

    critical_controls = sum(
        1
        for item in items
        if item["health_state"]
        == "CRITICAL"
    )

    ineffective_controls = sum(
        1
        for item in items
        if item["effectiveness"]
        <= INEFFECTIVE_CONTROL_THRESHOLD
    )

    controls_without_evidence = sum(
        1
        for item in items
        if item["evidence_count"] == 0
    )

    stale_evidence = sum(
        item["stale_evidence"]
        for item in items
    )

    framework_mapped_controls = sum(
        1
        for item in items
        if item["framework_count"] > 0
    )

    risk_mapped_controls = sum(
        1
        for item in items
        if item["risk_count"] > 0
    )

    remediation_required = sum(
        1
        for item in items
        if item["remediation_required"]
    )

    open_exceptions = sum(
        item["open_finding_count"]
        for item in items
    )

    critical_exceptions = sum(
        item["critical_finding_count"]
        for item in items
    )

    active_controls = sum(
        1
        for item in items
        if item["status"] == "Active"
    )

    average_effectiveness = (
        round(
            sum(
                item["effectiveness"]
                for item in items
            )
            / total_controls,
            1,
        )
        if total_controls
        else 0
    )

    average_health_score = (
        round(
            sum(
                item["health_score"]
                for item in items
            )
            / total_controls,
            1,
        )
        if total_controls
        else 0
    )

    evidence_coverage_percent = (
        round(
            (
                total_controls
                - controls_without_evidence
            )
            / total_controls
            * 100,
            1,
        )
        if total_controls
        else 0
    )

    framework_coverage_percent = (
        round(
            framework_mapped_controls
            / total_controls
            * 100,
            1,
        )
        if total_controls
        else 0
    )

    risk_coverage_percent = (
        round(
            risk_mapped_controls
            / total_controls
            * 100,
            1,
        )
        if total_controls
        else 0
    )

    if critical_controls > 0:
        overall_posture = "CRITICAL"

    elif degraded_controls > 0:
        overall_posture = "DEGRADED"

    else:
        overall_posture = "HEALTHY"

    # Highest-priority controls first.
    priority_order = {
        "CRITICAL": 0,
        "DEGRADED": 1,
        "HEALTHY": 2,
    }

    prioritized_items = sorted(
        items,
        key=lambda item: (
            priority_order.get(
                item["health_state"],
                9,
            ),
            -item["effectiveness"],
            item["control_id"],
        ),
    )

    return {
        "generated_at": now,
        "summary": {
            "total_controls": total_controls,
            "active_controls": active_controls,
            "healthy_controls": healthy_controls,
            "degraded_controls": degraded_controls,
            "critical_controls": critical_controls,
            "ineffective_controls": ineffective_controls,
            "controls_without_evidence": controls_without_evidence,
            "stale_evidence": stale_evidence,
            "framework_mapped_controls": (
                framework_mapped_controls
            ),
            "risk_mapped_controls": (
                risk_mapped_controls
            ),
            "evidence_coverage_percent": (
                evidence_coverage_percent
            ),
            "framework_coverage_percent": (
                framework_coverage_percent
            ),
            "risk_coverage_percent": (
                risk_coverage_percent
            ),
            "average_effectiveness": (
                average_effectiveness
            ),
            "average_health_score": (
                average_health_score
            ),
            "open_exceptions": open_exceptions,
            "critical_exceptions": (
                critical_exceptions
            ),
            "remediation_required": (
                remediation_required
            ),
            "overall_posture": overall_posture,
        },
        "controls": prioritized_items,
    }