"""
Evidence Intelligence Service

Phase 62
--------

Deterministic, read-only intelligence over the existing Evidence,
Control, RiskControl and Risk models.

This service intentionally does not introduce new Evidence state into
the database. Intelligence is derived from authoritative GRC records.

Capabilities:
- Evidence freshness
- Evidence completeness
- Evidence quality
- Evidence -> Control mapping
- Evidence -> Risk mapping
- Missing evidence detection
- Evidence coverage
- Evidence collection recommendations
- Audit-readiness / audit-package intelligence

Governance boundary:
- Read-only
- No underlying GRC mutation
- No autonomous evidence collection
- No autonomous audit closure
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Iterable

from sqlalchemy.orm import Session

from app.models.control import Control
from app.models.evidence import Evidence
from app.models.risk import Risk
from app.models.risk_control import RiskControl


# ==========================================================
# Phase 62 - Thresholds
# ==========================================================

EVIDENCE_FRESH_DAYS = 30
EVIDENCE_AGING_DAYS = 90

HIGH_QUALITY_THRESHOLD = 80
ACCEPTABLE_QUALITY_THRESHOLD = 60


# ==========================================================
# Enums
# ==========================================================


class EvidenceFreshness(str, Enum):
    FRESH = "FRESH"
    AGING = "AGING"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


class EvidenceQuality(str, Enum):
    HIGH = "HIGH"
    ACCEPTABLE = "ACCEPTABLE"
    LOW = "LOW"


class EvidenceCompleteness(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    INCOMPLETE = "INCOMPLETE"


class EvidenceCollectionPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ==========================================================
# Dataclasses
# ==========================================================


@dataclass(frozen=True)
class EvidenceIntelligence:
    evidence_id: int
    control_id: int
    risk_ids: tuple[int, ...]

    age_days: float | None

    freshness: EvidenceFreshness
    freshness_score: int

    completeness: EvidenceCompleteness
    completeness_score: int

    quality: EvidenceQuality
    quality_score: int

    quality_indicators: tuple[str, ...]

    evidence_to_control_mapped: bool
    evidence_to_risk_mapped: bool

    file_available: bool


@dataclass(frozen=True)
class MissingEvidenceIntelligence:
    control_id: int
    control_title: str
    priority: EvidenceCollectionPriority
    reason: str
    recommended_action: str


@dataclass(frozen=True)
class EvidenceCollectionWorkflow:
    control_id: int
    control_title: str
    priority: EvidenceCollectionPriority
    workflow_type: str
    status: str
    recommended_action: str


@dataclass(frozen=True)
class EvidenceCoverageIntelligence:
    total_controls: int
    controls_with_evidence: int
    controls_without_evidence: int
    coverage_percent: float

    total_evidence: int
    fresh_evidence: int
    aging_evidence: int
    stale_evidence: int

    risk_mapped_evidence: int

    average_quality_score: float
    average_completeness_score: float

    audit_readiness_score: float
    audit_ready: bool


@dataclass(frozen=True)
class EvidenceIntelligenceReport:
    coverage: EvidenceCoverageIntelligence
    evidence: tuple[EvidenceIntelligence, ...]
    missing_evidence: tuple[MissingEvidenceIntelligence, ...]
    collection_workflows: tuple[EvidenceCollectionWorkflow, ...]
    audit_package_evidence_ids: tuple[int, ...]


# ==========================================================
# Time helpers
# ==========================================================


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value


def _calculate_age_days(
    uploaded_at: datetime | None,
    now: datetime,
) -> float | None:
    timestamp = _ensure_aware(uploaded_at)

    if timestamp is None:
        return None

    elapsed = now - timestamp

    return max(
        0.0,
        elapsed.total_seconds() / 86400.0,
    )


# ==========================================================
# Freshness
# ==========================================================


def derive_evidence_freshness(
    age_days: float | None,
) -> tuple[EvidenceFreshness, int]:
    """
    Determine evidence freshness from age.

    <= 30 days:
        FRESH

    > 30 and <= 90 days:
        AGING

    > 90 days:
        STALE

    Missing timestamp:
        UNKNOWN
    """

    if age_days is None:
        return (
            EvidenceFreshness.UNKNOWN,
            0,
        )

    if age_days <= EVIDENCE_FRESH_DAYS:
        return (
            EvidenceFreshness.FRESH,
            100,
        )

    if age_days <= EVIDENCE_AGING_DAYS:
        # Linear degradation from 100 toward 50.
        ratio = (
            age_days - EVIDENCE_FRESH_DAYS
        ) / (
            EVIDENCE_AGING_DAYS
            - EVIDENCE_FRESH_DAYS
        )

        score = int(
            round(
                100
                - (
                    ratio * 50
                )
            )
        )

        return (
            EvidenceFreshness.AGING,
            max(50, min(99, score)),
        )

    # Stale evidence continues to lose freshness
    # but is capped at zero.
    stale_days = age_days - EVIDENCE_AGING_DAYS

    score = max(
        0,
        int(
            round(
                50
                - min(
                    50,
                    stale_days / 2,
                )
            )
        ),
    )

    return (
        EvidenceFreshness.STALE,
        score,
    )


# ==========================================================
# Completeness
# ==========================================================


def derive_evidence_completeness(
    evidence: Evidence,
    *,
    file_available: bool,
) -> tuple[EvidenceCompleteness, int]:
    """
    Evaluate the completeness of the evidence record.

    Required attributes:
    - title
    - description
    - file name
    - control mapping
    - uploader
    - physical file availability
    """

    checks = (
        bool(
            str(
                getattr(
                    evidence,
                    "title",
                    "",
                )
                or ""
            ).strip()
        ),
        bool(
            str(
                getattr(
                    evidence,
                    "description",
                    "",
                )
                or ""
            ).strip()
        ),
        bool(
            str(
                getattr(
                    evidence,
                    "file_name",
                    "",
                )
                or ""
            ).strip()
        ),
        getattr(
            evidence,
            "control_id",
            None,
        )
        is not None,
        getattr(
            evidence,
            "uploaded_by",
            None,
        )
        is not None,
        file_available,
    )

    score = int(
        round(
            (
                sum(
                    1
                    for check in checks
                    if check
                )
                / len(checks)
            )
            * 100
        )
    )

    if score == 100:
        return (
            EvidenceCompleteness.COMPLETE,
            score,
        )

    if score >= 60:
        return (
            EvidenceCompleteness.PARTIAL,
            score,
        )

    return (
        EvidenceCompleteness.INCOMPLETE,
        score,
    )


# ==========================================================
# Quality
# ==========================================================


def derive_evidence_quality(
    *,
    freshness_score: int,
    completeness_score: int,
    control_mapped: bool,
    risk_mapped: bool,
) -> tuple[
    EvidenceQuality,
    int,
    tuple[str, ...],
]:
    """
    Produce a deterministic quality score.

    Weighting:
        Freshness     40%
        Completeness  40%
        Mapping       20%

    Risk mapping contributes to the mapping quality indicator
    but does not make risk mapping mandatory for evidence.
    """

    mapping_score = 0

    if control_mapped:
        mapping_score += 70

    if risk_mapped:
        mapping_score += 30

    score = int(
        round(
            (
                freshness_score * 0.40
            )
            + (
                completeness_score * 0.40
            )
            + (
                mapping_score * 0.20
            )
        )
    )

    indicators: list[str] = []

    if freshness_score >= 80:
        indicators.append(
            "Evidence is sufficiently fresh."
        )
    elif freshness_score >= 50:
        indicators.append(
            "Evidence is ageing and should be reviewed."
        )
    else:
        indicators.append(
            "Evidence is stale and requires attention."
        )

    if completeness_score == 100:
        indicators.append(
            "Evidence metadata and file availability are complete."
        )
    elif completeness_score >= 60:
        indicators.append(
            "Evidence metadata or file availability is partially incomplete."
        )
    else:
        indicators.append(
            "Evidence record is materially incomplete."
        )

    if control_mapped:
        indicators.append(
            "Evidence is mapped to a control."
        )
    else:
        indicators.append(
            "Evidence has no valid control mapping."
        )

    if risk_mapped:
        indicators.append(
            "Evidence supports at least one risk through control mapping."
        )
    else:
        indicators.append(
            "Evidence is not currently connected to a risk."
        )

    if score >= HIGH_QUALITY_THRESHOLD:
        quality = EvidenceQuality.HIGH
    elif score >= ACCEPTABLE_QUALITY_THRESHOLD:
        quality = EvidenceQuality.ACCEPTABLE
    else:
        quality = EvidenceQuality.LOW

    return (
        quality,
        max(0, min(100, score)),
        tuple(indicators),
    )


# ==========================================================
# File availability
# ==========================================================


def _evidence_file_available(
    evidence: Evidence,
) -> bool:
    file_path = getattr(
        evidence,
        "file_path",
        None,
    )

    if not file_path:
        return False

    try:
        path = Path(str(file_path))

        if not path.is_absolute():
            path = Path.cwd() / path

        return path.is_file()

    except (OSError, ValueError):
        return False


# ==========================================================
# Evidence -> Risk mapping
# ==========================================================


def _get_risk_ids_for_control(
    db: Session,
    control_id: int,
) -> tuple[int, ...]:
    rows = (
        db.query(RiskControl.risk_id)
        .join(
            Risk,
            Risk.id == RiskControl.risk_id,
        )
        .filter(
            RiskControl.control_id == control_id,
        )
        .order_by(
            RiskControl.risk_id.asc()
        )
        .all()
    )

    return tuple(
        int(row[0])
        for row in rows
    )


# ==========================================================
# Single evidence intelligence
# ==========================================================


def get_evidence_intelligence(
    db: Session,
    evidence: Evidence,
    *,
    now: datetime | None = None,
) -> EvidenceIntelligence:
    current_time = (
        now
        if now is not None
        else _now_utc()
    )

    age_days = _calculate_age_days(
        getattr(
            evidence,
            "uploaded_at",
            None,
        ),
        current_time,
    )

    freshness, freshness_score = (
        derive_evidence_freshness(
            age_days
        )
    )

    file_available = (
        _evidence_file_available(
            evidence
        )
    )

    completeness, completeness_score = (
        derive_evidence_completeness(
            evidence,
            file_available=file_available,
        )
    )

    control_mapped = (
        getattr(
            evidence,
            "control_id",
            None,
        )
        is not None
    )

    risk_ids = (
        _get_risk_ids_for_control(
            db,
            int(evidence.control_id),
        )
        if control_mapped
        else ()
    )

    risk_mapped = bool(risk_ids)

    quality, quality_score, indicators = (
        derive_evidence_quality(
            freshness_score=freshness_score,
            completeness_score=completeness_score,
            control_mapped=control_mapped,
            risk_mapped=risk_mapped,
        )
    )

    return EvidenceIntelligence(
        evidence_id=int(evidence.id),
        control_id=int(evidence.control_id),
        risk_ids=risk_ids,
        age_days=age_days,
        freshness=freshness,
        freshness_score=freshness_score,
        completeness=completeness,
        completeness_score=completeness_score,
        quality=quality,
        quality_score=quality_score,
        quality_indicators=indicators,
        evidence_to_control_mapped=control_mapped,
        evidence_to_risk_mapped=risk_mapped,
        file_available=file_available,
    )


# ==========================================================
# Missing evidence
# ==========================================================


def _derive_collection_priority(
    control: Control,
) -> EvidenceCollectionPriority:
    """
    Derive a deterministic collection priority.

    Critical:
        inactive/critical control state

    High:
        low effectiveness

    Medium:
        active control without evidence

    Low:
        other controls
    """

    status = str(
        getattr(
            control,
            "status",
            "",
        )
        or ""
    ).strip().lower()

    effectiveness = int(
        getattr(
            control,
            "effectiveness",
            0,
        )
        or 0
    )

    if status in {
        "inactive",
        "critical",
    }:
        return EvidenceCollectionPriority.CRITICAL

    if effectiveness < 50:
        return EvidenceCollectionPriority.HIGH

    if effectiveness < 75:
        return EvidenceCollectionPriority.MEDIUM

    return EvidenceCollectionPriority.LOW


def detect_missing_evidence(
    controls: Iterable[Control],
) -> tuple[MissingEvidenceIntelligence, ...]:
    missing: list[
        MissingEvidenceIntelligence
    ] = []

    for control in controls:
        evidence_items = getattr(
            control,
            "evidence",
            None,
        )

        if evidence_items:
            continue

        priority = _derive_collection_priority(
            control
        )

        missing.append(
            MissingEvidenceIntelligence(
                control_id=int(control.id),
                control_title=str(
                    control.title
                ),
                priority=priority,
                reason=(
                    "No evidence is currently "
                    "mapped to this control."
                ),
                recommended_action=(
                    "Collect and attach current "
                    "supporting evidence."
                ),
            )
        )

    missing.sort(
        key=lambda item: (
            {
                EvidenceCollectionPriority.CRITICAL: 4,
                EvidenceCollectionPriority.HIGH: 3,
                EvidenceCollectionPriority.MEDIUM: 2,
                EvidenceCollectionPriority.LOW: 1,
            }[item.priority],
            item.control_id,
        ),
        reverse=True,
    )

    return tuple(missing)


# ==========================================================
# Coverage
# ==========================================================


def calculate_evidence_coverage(
    controls: Iterable[Control],
    evidence_items: Iterable[
        EvidenceIntelligence
    ],
) -> EvidenceCoverageIntelligence:
    controls_list = list(controls)
    evidence_list = list(evidence_items)

    total_controls = len(
        controls_list
    )

    controls_with_evidence = len(
        {
            item.control_id
            for item in evidence_list
        }
    )

    controls_without_evidence = max(
        0,
        total_controls
        - controls_with_evidence,
    )

    coverage_percent = (
        (
            controls_with_evidence
            / total_controls
        )
        * 100
        if total_controls
        else 100.0
    )

    fresh_count = sum(
        1
        for item in evidence_list
        if item.freshness
        == EvidenceFreshness.FRESH
    )

    aging_count = sum(
        1
        for item in evidence_list
        if item.freshness
        == EvidenceFreshness.AGING
    )

    stale_count = sum(
        1
        for item in evidence_list
        if item.freshness
        == EvidenceFreshness.STALE
    )

    risk_mapped_count = sum(
        1
        for item in evidence_list
        if item.evidence_to_risk_mapped
    )

    average_quality = (
        sum(
            item.quality_score
            for item in evidence_list
        )
        / len(evidence_list)
        if evidence_list
        else 0.0
    )

    average_completeness = (
        sum(
            item.completeness_score
            for item in evidence_list
        )
        / len(evidence_list)
        if evidence_list
        else 0.0
    )

    freshness_component = (
        (
            (
                fresh_count
                + (
                    aging_count * 0.5
                )
            )
            / len(evidence_list)
        )
        * 100
        if evidence_list
        else 0.0
    )

    audit_readiness_score = round(
        (
            coverage_percent * 0.40
        )
        + (
            average_quality * 0.35
        )
        + (
            average_completeness * 0.15
        )
        + (
            freshness_component * 0.10
        ),
        2,
    )

    audit_ready = (
        controls_without_evidence == 0
        and stale_count == 0
        and average_quality
        >= ACCEPTABLE_QUALITY_THRESHOLD
    )

    return EvidenceCoverageIntelligence(
        total_controls=total_controls,
        controls_with_evidence=controls_with_evidence,
        controls_without_evidence=controls_without_evidence,
        coverage_percent=round(
            coverage_percent,
            2,
        ),
        total_evidence=len(
            evidence_list
        ),
        fresh_evidence=fresh_count,
        aging_evidence=aging_count,
        stale_evidence=stale_count,
        risk_mapped_evidence=risk_mapped_count,
        average_quality_score=round(
            average_quality,
            2,
        ),
        average_completeness_score=round(
            average_completeness,
            2,
        ),
        audit_readiness_score=round(
            audit_readiness_score,
            2,
        ),
        audit_ready=audit_ready,
    )


# ==========================================================
# Full report
# ==========================================================


def build_evidence_intelligence_report(
    db: Session,
    *,
    visible_user_ids: Iterable[int],
    now: datetime | None = None,
) -> EvidenceIntelligenceReport:
    """
    Build the complete Phase 62 evidence intelligence report.

    Visibility is supplied by the caller so this service does not
    bypass the existing RBAC/visibility architecture.
    """

    user_ids = tuple(
        int(user_id)
        for user_id in visible_user_ids
    )

    controls = (
        db.query(Control)
        .filter(
            Control.owner_id.in_(
                user_ids
            )
        )
        .order_by(
            Control.id.asc()
        )
        .all()
    )

    evidence_rows = (
        db.query(Evidence)
        .join(
            Control,
            Evidence.control_id
            == Control.id,
        )
        .filter(
            Control.owner_id.in_(
                user_ids
            )
        )
        .order_by(
            Evidence.id.asc()
        )
        .all()
    )

    evidence_intelligence = tuple(
        get_evidence_intelligence(
            db,
            evidence,
            now=now,
        )
        for evidence in evidence_rows
    )

    missing = detect_missing_evidence(
        controls
    )

    coverage = calculate_evidence_coverage(
        controls,
        evidence_intelligence,
    )

    collection_workflows = tuple(
        EvidenceCollectionWorkflow(
            control_id=item.control_id,
            control_title=item.control_title,
            priority=item.priority,
            workflow_type="EVIDENCE_COLLECTION",
            status="RECOMMENDED",
            recommended_action=item.recommended_action,
        )
        for item in missing
    )

    audit_package_evidence_ids = tuple(
        item.evidence_id
        for item in evidence_intelligence
        if (
            item.completeness
            == EvidenceCompleteness.COMPLETE
            and item.freshness
            != EvidenceFreshness.STALE
        )
    )

    return EvidenceIntelligenceReport(
        coverage=coverage,
        evidence=evidence_intelligence,
        missing_evidence=missing,
        collection_workflows=collection_workflows,
        audit_package_evidence_ids=(
            audit_package_evidence_ids
        ),
    )