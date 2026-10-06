from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_finding import AuditFinding
from app.models.control import Control
from app.models.corrective_action import CorrectiveAction
from app.models.evidence import Evidence
from app.models.framework import Framework
from app.models.framework_control import FrameworkControl
from app.models.risk import Risk
from app.models.risk_control import RiskControl
from app.models.user import User

from app.services.control_intelligence_service import (
    build_control_intelligence_report,
)
from app.services.regulatory_intelligence_service import (
    build_regulatory_intelligence_report,
)


HIGH_RISK_SCORE = 15
CRITICAL_RISK_SCORE = 20

INEFFECTIVE_CONTROL_THRESHOLD = 50
DEGRADED_CONTROL_THRESHOLD = 70

STALE_EVIDENCE_DAYS = 90


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _is_open_finding(finding: AuditFinding) -> bool:
    status = str(getattr(finding, "status", "")).upper()

    return status not in {
        "CLOSED",
        "RESOLVED",
        "REMEDIATED",
        "VERIFIED",
    }


def _is_open_action(action: CorrectiveAction) -> bool:
    status = str(getattr(action, "status", "")).upper()

    return status not in {
        "CLOSED",
        "COMPLETED",
        "RESOLVED",
    }


def _risk_state(risk: Risk) -> str:
    score = getattr(risk, "risk_score", None)

    if score is None:
        return "UNKNOWN"

    if score >= CRITICAL_RISK_SCORE:
        return "CRITICAL"

    if score >= HIGH_RISK_SCORE:
        return "HIGH"

    return "MEDIUM_LOW"


def _control_state(control: Control) -> str:
    effectiveness = getattr(control, "effectiveness", None)

    if not getattr(control, "is_active", True):
        return "INACTIVE"

    if effectiveness is None:
        return "UNKNOWN"

    if effectiveness < INEFFECTIVE_CONTROL_THRESHOLD:
        return "INEFFECTIVE"

    if effectiveness < DEGRADED_CONTROL_THRESHOLD:
        return "DEGRADED"

    if effectiveness >= 80:
        return "HEALTHY"

    return "ADEQUATE"


def _evidence_state(
    evidence: list[Evidence],
) -> str:
    if not evidence:
        return "MISSING"

    now = _utcnow()

    stale = 0

    for item in evidence:
        uploaded_at = getattr(item, "uploaded_at", None)

        if uploaded_at is None:
            stale += 1
            continue

        if uploaded_at.tzinfo is None:
            uploaded_at = uploaded_at.replace(
                tzinfo=timezone.utc
            )

        age_days = (
            now - uploaded_at
        ).total_seconds() / 86400

        if age_days > STALE_EVIDENCE_DAYS:
            stale += 1

    if stale == len(evidence):
        return "STALE"

    if stale > 0:
        return "MIXED"

    return "CURRENT"


def _risk_payload(risk: Risk) -> dict[str, Any]:
    return {
        "id": risk.id,
        "title": getattr(risk, "title", None),
        "description": getattr(risk, "description", None),
        "score": getattr(risk, "risk_score", None),
        "status": getattr(risk, "status", None),
        "state": _risk_state(risk),
    }


def _control_payload(
    control: Control,
    evidence: list[Evidence],
) -> dict[str, Any]:
    return {
        "id": control.id,
        "title": getattr(control, "title", None),
        "description": getattr(control, "description", None),
        "effectiveness": getattr(
            control,
            "effectiveness",
            None,
        ),
        "state": _control_state(control),
        "evidence_state": _evidence_state(
            evidence
        ),
    }


def build_ai_grc_analyst_context(
    db: Session,
    visible_user_ids: list[int],
) -> dict[str, Any]:
    """
    Build a deterministic GRC context for the AI analyst.

    This function does not call an LLM.

    Its purpose is to ensure the model receives only
    governed, visibility-filtered GRC information.
    """

    risks = (
        db.query(Risk)
        .filter(
            Risk.owner_id.in_(visible_user_ids)
        )
        .all()
    )

    controls = (
        db.query(Control)
        .filter(
            Control.owner_id.in_(visible_user_ids)
        )
        .all()
    )

    findings = (
        db.query(AuditFinding)
        .all()
    )

    actions = (
        db.query(CorrectiveAction)
        .all()
    )

    evidence = (
        db.query(Evidence)
        .filter(
            Evidence.uploaded_by.in_(
                visible_user_ids
            )
        )
        .all()
    )

    risk_controls = db.query(
        RiskControl
    ).all()

    control_risk_ids: dict[int, set[int]] = {}

    for mapping in risk_controls:
        control_risk_ids.setdefault(
            mapping.control_id,
            set(),
        ).add(mapping.risk_id)

    evidence_by_control: dict[
        int,
        list[Evidence],
    ] = {}

    for item in evidence:
        evidence_by_control.setdefault(
            item.control_id,
            [],
        ).append(item)

    visible_control_ids = {
        control.id
        for control in controls
    }

    visible_risks = {
        risk.id
        for risk in risks
    }

    mapped_risks: dict[int, list[int]] = {}

    for control_id, risk_ids in control_risk_ids.items():
        if control_id not in visible_control_ids:
            continue

        mapped_risks[control_id] = [
            risk_id
            for risk_id in risk_ids
            if risk_id in visible_risks
        ]

    critical_risks = [
        _risk_payload(risk)
        for risk in risks
        if _risk_state(risk) == "CRITICAL"
    ]

    high_risks = [
        _risk_payload(risk)
        for risk in risks
        if _risk_state(risk) == "HIGH"
    ]

    ineffective_controls = [
        _control_payload(
            control,
            evidence_by_control.get(
                control.id,
                [],
            ),
        )
        for control in controls
        if _control_state(control)
        == "INEFFECTIVE"
    ]

    degraded_controls = [
        _control_payload(
            control,
            evidence_by_control.get(
                control.id,
                [],
            ),
        )
        for control in controls
        if _control_state(control)
        == "DEGRADED"
    ]

    missing_evidence_controls = [
        control.id
        for control in controls
        if _evidence_state(
            evidence_by_control.get(
                control.id,
                [],
            )
        )
        == "MISSING"
    ]

    stale_evidence_controls = [
        control.id
        for control in controls
        if _evidence_state(
            evidence_by_control.get(
                control.id,
                [],
            )
        )
        in {"STALE", "MIXED"}
    ]

    open_findings = [
        finding
        for finding in findings
        if _is_open_finding(finding)
    ]

    open_actions = [
        action
        for action in actions
        if _is_open_action(action)
    ]

    regulatory = (
        build_regulatory_intelligence_report(
            db,
            visible_user_ids,
        )
    )

    control_intelligence = (
        build_control_intelligence_report(
            db,
            visible_user_ids,
        )
    )

    finding_severity = Counter(
        str(
            getattr(
                finding,
                "severity",
                "UNKNOWN",
            )
        ).upper()
        for finding in open_findings
    )

    return {
        "generated_at": _utcnow().isoformat(),

        "scope": {
            "visible_user_count": len(
                visible_user_ids
            ),
            "visible_risk_count": len(
                risks
            ),
            "visible_control_count": len(
                controls
            ),
        },

        "risk_summary": {
            "critical": len(
                critical_risks
            ),
            "high": len(high_risks),
            "total": len(risks),
            "critical_risks": critical_risks[:10],
            "high_risks": high_risks[:10],
        },

        "control_summary": {
            "total": len(controls),
            "ineffective": len(
                ineffective_controls
            ),
            "degraded": len(
                degraded_controls
            ),
            "missing_evidence": len(
                missing_evidence_controls
            ),
            "stale_evidence": len(
                stale_evidence_controls
            ),
            "ineffective_controls":
                ineffective_controls[:10],
            "degraded_controls":
                degraded_controls[:10],
        },

        "evidence_summary": {
            "total": len(evidence),
            "controls_missing_evidence":
                missing_evidence_controls[:20],
            "controls_with_stale_evidence":
                stale_evidence_controls[:20],
        },

        "finding_summary": {
            "open": len(open_findings),
            "severity": dict(
                finding_severity
            ),
        },

        "corrective_action_summary": {
            "open": len(open_actions),
        },

        "risk_control_mapping": {
            str(control_id): risk_ids
            for control_id, risk_ids
            in mapped_risks.items()
        },

        "regulatory_summary": {
            "overall_posture":
                getattr(
                    regulatory,
                    "overall_posture",
                    None,
                ),
            "overall_coverage_percentage":
                getattr(
                    regulatory,
                    "overall_coverage_percentage",
                    None,
                ),
            "critical_requirements":
                getattr(
                    regulatory,
                    "critical_requirements",
                    0,
                ),
            "high_requirements":
                getattr(
                    regulatory,
                    "high_requirements",
                    0,
                ),
            "gap_requirements":
                getattr(
                    regulatory,
                    "gap_requirements",
                    0,
                ),
            "partial_requirements":
                getattr(
                    regulatory,
                    "partial_requirements",
                    0,
                ),
        },

        "control_intelligence_summary": {
            "overall_posture":
                getattr(
                    control_intelligence,
                    "overall_posture",
                    None,
                ),
            "total_controls":
                getattr(
                    control_intelligence,
                    "total_controls",
                    0,
                ),
            "critical_controls":
                getattr(
                    control_intelligence,
                    "critical_controls",
                    0,
                ),
            "degraded_controls":
                getattr(
                    control_intelligence,
                    "degraded_controls",
                    0,
                ),
        },
    }


def get_analyst_question_category(
    question: str,
) -> str:
    normalized = question.lower()

    if any(
        value in normalized
        for value in [
            "compliance",
            "regulation",
            "regulatory",
            "dora",
            "gdpr",
            "nis2",
            "iso",
            "nist",
        ]
    ):
        return "REGULATORY"

    if any(
        value in normalized
        for value in [
            "control",
            "ineffective",
            "effectiveness",
        ]
    ):
        return "CONTROL"

    if any(
        value in normalized
        for value in [
            "evidence",
            "proof",
            "document",
        ]
    ):
        return "EVIDENCE"

    if any(
        value in normalized
        for value in [
            "finding",
            "corrective",
            "remediation",
        ]
    ):
        return "ASSURANCE"

    if any(
        value in normalized
        for value in [
            "risk",
            "risks",
            "exposure",
        ]
    ):
        return "RISK"

    return "GENERAL"


def build_analyst_prompt(
    question: str,
    context: dict[str, Any],
) -> str:
    return f"""
You are the AI GRC Analyst for a cybersecurity
governance platform.

You are an analytical assistant, not an autonomous
decision maker.

Use ONLY the supplied GRC context.

Do not invent:
- risks
- controls
- evidence
- regulatory requirements
- findings
- business facts
- compliance status

If the supplied context does not contain enough
information, explicitly say so.

Your responsibilities:
1. Identify the most relevant GRC facts.
2. Explain why they matter.
3. Identify material risks or gaps.
4. Recommend sensible next steps.
5. Clearly distinguish facts from recommendations.
6. Never claim that remediation has been performed.
7. Never instruct the system to autonomously
   modify GRC resources.

Every recommendation requires human review.

User question:
{question}

GRC context:
{context}

Return a concise professional GRC analysis.
""".strip()