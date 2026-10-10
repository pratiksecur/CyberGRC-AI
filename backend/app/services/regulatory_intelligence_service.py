from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.control import Control
from app.models.control_framework_control import (
    ControlFrameworkControl,
)
from app.models.evidence import Evidence
from app.models.framework import Framework
from app.models.framework_control import FrameworkControl
from app.models.risk import Risk
from app.models.risk_control import RiskControl


CONTROL_CRITICAL_THRESHOLD = 50
CONTROL_DEGRADED_THRESHOLD = 70
CONTROL_HEALTHY_THRESHOLD = 80

EVIDENCE_AGING_DAYS = 30
EVIDENCE_STALE_DAYS = 90

HIGH_RISK_SCORE = 15
CRITICAL_RISK_SCORE = 20


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value


def _evidence_age(
    uploaded_at: datetime | None,
    now: datetime,
) -> int | None:

    uploaded_at = _aware(uploaded_at)

    if uploaded_at is None:
        return None

    return max(
        0,
        (now - uploaded_at).days,
    )


def _control_state(control: Control) -> str:

    status = (
        control.status or ""
    ).strip().lower()

    effectiveness = int(
        control.effectiveness or 0
    )

    if status != "active":
        return "INACTIVE"

    if effectiveness < CONTROL_CRITICAL_THRESHOLD:
        return "CRITICAL"

    if effectiveness < CONTROL_DEGRADED_THRESHOLD:
        return "DEGRADED"

    if effectiveness >= CONTROL_HEALTHY_THRESHOLD:
        return "HEALTHY"

    return "ADEQUATE"


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
            "freshness_score": 0.0,
            "state": "MISSING",
        }

    fresh = 0
    aging = 0
    stale = 0
    scores: list[float] = []

    for item in evidence:

        age = _evidence_age(
            item.uploaded_at,
            now,
        )

        if age is None:
            stale += 1
            scores.append(0.0)
            continue

        if age <= EVIDENCE_AGING_DAYS:
            fresh += 1
            scores.append(100.0)

        elif age <= EVIDENCE_STALE_DAYS:
            aging += 1

            score = max(
                50.0,
                100.0
                - (
                    (
                        age
                        - EVIDENCE_AGING_DAYS
                    )
                    / (
                        EVIDENCE_STALE_DAYS
                        - EVIDENCE_AGING_DAYS
                    )
                    * 50.0
                ),
            )

            scores.append(score)

        else:
            stale += 1

            score = max(
                0.0,
                50.0
                - (
                    (
                        age
                        - EVIDENCE_STALE_DAYS
                    )
                    / EVIDENCE_STALE_DAYS
                    * 50.0
                ),
            )

            scores.append(score)

    freshness_score = (
        sum(scores) / len(scores)
        if scores
        else 0.0
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
            freshness_score,
            1,
        ),
        "state": state,
    }


def _get_controls_for_requirement(
    db: Session,
    framework_control_id: int,
    visible_user_ids: set[int],
) -> list[Control]:

    return (
        db.query(Control)
        .join(
            ControlFrameworkControl,
            ControlFrameworkControl.control_id
            == Control.id,
        )
        .filter(
            ControlFrameworkControl.framework_control_id
            == framework_control_id,
            Control.owner_id.in_(
                visible_user_ids
            ),
        )
        .order_by(Control.id.asc())
        .all()
    )


def _get_evidence_for_control(
    db: Session,
    control_id: int,
    visible_user_ids: set[int],
) -> list[Evidence]:

    return (
        db.query(Evidence)
        .filter(
            Evidence.control_id == control_id,
            Evidence.uploaded_by.in_(
                visible_user_ids
            ),
        )
        .order_by(
            Evidence.uploaded_at.desc(),
            Evidence.id.desc(),
        )
        .all()
    )


def _get_risks_for_control(
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


def _risk_exposure(
    risks: list[Risk],
) -> str:

    if not risks:
        return "NONE"

    maximum = max(
        int(risk.risk_score or 0)
        for risk in risks
    )

    if maximum >= CRITICAL_RISK_SCORE:
        return "CRITICAL"

    if maximum >= HIGH_RISK_SCORE:
        return "HIGH"

    return "MEDIUM"


def _requirement_state(
    controls: list[dict[str, Any]],
) -> str:

    if not controls:
        return "GAP"

    if all(
        item["control_state"] == "HEALTHY"
        and item["evidence_state"] == "FRESH"
        for item in controls
    ):
        return "COVERED"

    return "PARTIAL"


def _requirement_exposure(
    controls: list[dict[str, Any]],
) -> str:

    if not controls:
        return "CRITICAL"

    if any(
        item["risk_exposure"] == "CRITICAL"
        for item in controls
    ):
        return "CRITICAL"

    if any(
        item["risk_exposure"] == "HIGH"
        for item in controls
    ):
        return "HIGH"

    if any(
        item["control_state"]
        == "CRITICAL"
        for item in controls
    ):
        return "HIGH"

    if any(
        item["evidence_state"]
        in {
            "MISSING",
            "STALE",
            "MIXED",
        }
        for item in controls
    ):
        return "MEDIUM"

    return "LOW"


def _control_intelligence(
    db: Session,
    control: Control,
    visible_user_ids: set[int],
    now: datetime,
) -> dict[str, Any]:

    evidence = _get_evidence_for_control(
        db,
        control.id,
        visible_user_ids,
    )

    risks = _get_risks_for_control(
        db,
        control.id,
        visible_user_ids,
    )

    evidence_info = _evidence_state(
        evidence,
        now,
    )

    return {
        "control_id": control.id,
        "control_title": control.title,
        "control_status": control.status,
        "effectiveness": int(
            control.effectiveness or 0
        ),
        "control_state": _control_state(
            control
        ),
        "evidence_count": len(evidence),
        "evidence_state": (
            evidence_info["state"]
        ),
        "evidence_freshness_score": (
            evidence_info[
                "freshness_score"
            ]
        ),
        "risk_ids": [
            risk.id
            for risk in risks
        ],
        "risk_scores": [
            int(risk.risk_score or 0)
            for risk in risks
        ],
        "risk_exposure": _risk_exposure(
            risks
        ),
    }


def get_regulatory_requirement_intelligence(
    db: Session,
    framework_control: FrameworkControl,
    visible_user_ids: set[int],
    now: datetime | None = None,
) -> dict[str, Any]:

    now = now or _utc_now()

    controls = _get_controls_for_requirement(
        db,
        framework_control.id,
        visible_user_ids,
    )

    control_data = [
        _control_intelligence(
            db,
            control,
            visible_user_ids,
            now,
        )
        for control in controls
    ]

    return {
        "requirement_id": framework_control.id,
        "requirement_code": (
            framework_control.control_code
        ),
        "requirement_title": (
            framework_control.title
        ),
        "requirement_description": (
            framework_control.description
        ),
        "mapped_control_count": len(
            control_data
        ),
        "control_ids": [
            item["control_id"]
            for item in control_data
        ],
        "controls": control_data,
        "state": _requirement_state(
            control_data
        ),
        "exposure": _requirement_exposure(
            control_data
        ),
    }


def _get_overlap_counts(
    db: Session,
    visible_user_ids: set[int],
) -> dict[int, int]:

    rows = (
        db.query(
            ControlFrameworkControl.control_id,
            FrameworkControl.framework_id,
        )
        .join(
            Control,
            Control.id
            == ControlFrameworkControl.control_id,
        )
        .join(
            FrameworkControl,
            FrameworkControl.id
            == ControlFrameworkControl.framework_control_id,
        )
        .filter(
            Control.owner_id.in_(
                visible_user_ids
            )
        )
        .all()
    )

    framework_ids: dict[
        int,
        set[int],
    ] = {}

    for control_id, framework_id in rows:
        framework_ids.setdefault(
            control_id,
            set(),
        ).add(framework_id)

    return {
        control_id: len(ids)
        for control_id, ids
        in framework_ids.items()
    }


def build_regulatory_intelligence_report(
    db: Session,
    visible_user_ids: set[int],
    now: datetime | None = None,
    organization_id: int | None = None,
) -> dict[str, Any]:

    now = now or _utc_now()

    framework_query = db.query(Framework)
    if organization_id is not None:
        framework_query = framework_query.filter(
            Framework.organization_id == organization_id
        )
    frameworks = framework_query.order_by(Framework.name.asc()).all()

    overlap_counts = _get_overlap_counts(
        db,
        visible_user_ids,
    )

    framework_reports = []

    total_requirements = 0
    covered_requirements = 0
    partial_requirements = 0
    gap_requirements = 0
    critical_requirements = 0
    high_requirements = 0

    for framework in frameworks:

        requirements = (
            db.query(FrameworkControl)
            .filter(
                FrameworkControl.framework_id
                == framework.id
            )
            .order_by(
                FrameworkControl.control_code.asc()
            )
            .all()
        )

        requirement_reports = []

        for requirement in requirements:

            requirement_report = (
                get_regulatory_requirement_intelligence(
                    db,
                    requirement,
                    visible_user_ids,
                    now,
                )
            )

            requirement_reports.append(
                requirement_report
            )

        total = len(requirement_reports)

        covered = sum(
            1
            for item in requirement_reports
            if item["state"] == "COVERED"
        )

        partial = sum(
            1
            for item in requirement_reports
            if item["state"] == "PARTIAL"
        )

        gaps = sum(
            1
            for item in requirement_reports
            if item["state"] == "GAP"
        )

        critical = sum(
            1
            for item in requirement_reports
            if item["exposure"] == "CRITICAL"
        )

        high = sum(
            1
            for item in requirement_reports
            if item["exposure"] == "HIGH"
        )

        coverage = (
            round(
                covered / total * 100,
                1,
            )
            if total
            else 100.0
        )

        framework_reports.append(
            {
                "framework_id": framework.id,
                "framework_name": framework.name,
                "framework_version": (
                    framework.version
                ),
                "requirement_count": total,
                "covered_requirements": covered,
                "partial_requirements": partial,
                "gap_requirements": gaps,
                "critical_requirements": critical,
                "high_requirements": high,
                "coverage_percent": coverage,
                "requirements": (
                    requirement_reports
                ),
            }
        )

        total_requirements += total
        covered_requirements += covered
        partial_requirements += partial
        gap_requirements += gaps
        critical_requirements += critical
        high_requirements += high

    overlapping_controls = sum(
        1
        for count in overlap_counts.values()
        if count > 1
    )

    overall_coverage = (
        round(
            covered_requirements
            / total_requirements
            * 100,
            1,
        )
        if total_requirements
        else 100.0
    )

    if critical_requirements:
        posture = "CRITICAL"
    elif gap_requirements:
        posture = "EXPOSED"
    elif partial_requirements:
        posture = "DEGRADED"
    else:
        posture = "HEALTHY"

    return {
        "generated_at": now,
        "framework_count": len(frameworks),
        "total_requirements": total_requirements,
        "covered_requirements": covered_requirements,
        "partial_requirements": partial_requirements,
        "gap_requirements": gap_requirements,
        "critical_requirements": critical_requirements,
        "high_requirements": high_requirements,
        "overall_coverage_percent": (
            overall_coverage
        ),
        "overall_posture": posture,
        "overlapping_controls": (
            overlapping_controls
        ),
        "frameworks": framework_reports,
    }