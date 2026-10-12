from datetime import datetime, timedelta, timezone

from app.models.control import Control
from app.models.evidence import Evidence
from app.models.risk import Risk
from app.models.risk_control import RiskControl
from app.services.evidence_intelligence_service import (
    EvidenceCompleteness,
    EvidenceFreshness,
    EvidenceQuality,
    calculate_evidence_coverage,
    derive_evidence_completeness,
    derive_evidence_freshness,
    derive_evidence_quality,
    get_evidence_intelligence,
)


def test_fresh_evidence_is_fresh():
    freshness, score = derive_evidence_freshness(
        10
    )

    assert freshness == EvidenceFreshness.FRESH
    assert score == 100


def test_ageing_evidence_is_ageing():
    freshness, score = derive_evidence_freshness(
        60
    )

    assert freshness == EvidenceFreshness.AGING
    assert 50 <= score < 100


def test_stale_evidence_is_stale():
    freshness, score = derive_evidence_freshness(
        120
    )

    assert freshness == EvidenceFreshness.STALE
    assert score < 50


def test_unknown_evidence_timestamp():
    freshness, score = derive_evidence_freshness(
        None
    )

    assert freshness == EvidenceFreshness.UNKNOWN
    assert score == 0


def test_complete_evidence_metadata():
    evidence = Evidence(
        id=1,
        control_id=1,
        title="Security Review",
        description="Supporting evidence",
        file_name="review.pdf",
        file_path="/does/not/matter.pdf",
        uploaded_by=1,
    )

    completeness, score = (
        derive_evidence_completeness(
            evidence,
            file_available=True,
        )
    )

    assert completeness == EvidenceCompleteness.COMPLETE
    assert score == 100


def test_partial_evidence_metadata():
    evidence = Evidence(
        id=1,
        control_id=1,
        title="",
        description="Supporting evidence",
        file_name="review.pdf",
        file_path="/does/not/matter.pdf",
        uploaded_by=1,
    )

    completeness, score = (
        derive_evidence_completeness(
            evidence,
            file_available=True,
        )
    )

    assert completeness == EvidenceCompleteness.PARTIAL
    assert 60 <= score < 100


def test_evidence_quality_is_deterministic():
    quality, score, indicators = (
        derive_evidence_quality(
            freshness_score=100,
            completeness_score=100,
            control_mapped=True,
            risk_mapped=True,
        )
    )

    assert quality == EvidenceQuality.HIGH
    assert score == 100
    assert indicators


def test_evidence_quality_identifies_stale_data():
    quality, score, indicators = (
        derive_evidence_quality(
            freshness_score=20,
            completeness_score=100,
            control_mapped=True,
            risk_mapped=False,
        )
    )

    assert quality != EvidenceQuality.HIGH
    assert score < 80
    assert any(
        "stale" in item.lower()
        for item in indicators
    )


def test_evidence_maps_to_risk(db, users):
    risk = Risk(
        title="Test Risk",
        description="Risk supported by control",
        likelihood=3,
        impact=4,
        risk_score=12,
        status="Open",
        owner_id=1,
        created_by_id=1,
    )

    control = Control(
        title="Security Control",
        description="Control",
        control_type="Preventive",
        status="Active",
        effectiveness=90,
        owner_id=1,
        created_by_id=1,
    )

    db.add_all(
        [
            risk,
            control,
        ]
    )
    db.commit()
    db.refresh(risk)
    db.refresh(control)

    risk_control = RiskControl(
        risk_id=risk.id,
        control_id=control.id,
    )

    evidence = Evidence(
        control_id=control.id,
        title="Evidence",
        description="Supporting evidence",
        file_name="evidence.pdf",
        file_path="/does/not/exist.pdf",
        uploaded_by=1,
    )

    db.add_all(
        [
            risk_control,
            evidence,
        ]
    )
    db.commit()
    db.refresh(evidence)

    intelligence = get_evidence_intelligence(
        db,
        evidence,
        now=datetime.now(timezone.utc),
    )

    assert intelligence.control_id == control.id
    assert intelligence.risk_ids == (
        risk.id,
    )
    assert (
        intelligence.evidence_to_control_mapped
        is True
    )
    assert (
        intelligence.evidence_to_risk_mapped
        is True
    )


def test_coverage_detects_missing_controls():
    control_a = Control(
        id=1,
        title="Control A",
        description="A",
        control_type="Preventive",
        status="Active",
        effectiveness=90,
        owner_id=1,
        created_by_id=1,
    )

    control_b = Control(
        id=2,
        title="Control B",
        description="B",
        control_type="Detective",
        status="Active",
        effectiveness=40,
        owner_id=1,
        created_by_id=1,
    )

    class Intelligence:
        def __init__(self):
            self.control_id = 1
            self.evidence_id = 1
            self.freshness = EvidenceFreshness.FRESH
            self.quality_score = 90
            self.completeness_score = 100
            self.evidence_to_risk_mapped = True

    coverage = calculate_evidence_coverage(
        [
            control_a,
            control_b,
        ],
        [
            Intelligence(),
        ],
    )

    assert coverage.total_controls == 2
    assert coverage.controls_with_evidence == 1
    assert coverage.controls_without_evidence == 1
    assert coverage.coverage_percent == 50.0
    assert coverage.audit_ready is False


def test_empty_evidence_set_is_not_a_failure():
    coverage = calculate_evidence_coverage(
        [],
        [],
    )

    assert coverage.total_controls == 0
    assert coverage.total_evidence == 0
    assert coverage.coverage_percent == 100.0
    assert coverage.audit_ready is False