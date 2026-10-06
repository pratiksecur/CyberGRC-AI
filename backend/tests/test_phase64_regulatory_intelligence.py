from datetime import datetime, timedelta, timezone

from app.models.control import Control
from app.models.control_framework_control import (
    ControlFrameworkControl,
)
from app.models.evidence import Evidence
from app.models.framework import Framework
from app.models.framework_control import (
    FrameworkControl,
)
from app.models.risk import Risk
from app.models.risk_control import RiskControl

from app.services.regulatory_intelligence_service import (
    build_regulatory_intelligence_report,
    get_regulatory_requirement_intelligence,
)


def test_requirement_without_control_is_gap(db):

    framework = Framework(
        name="Gap Framework",
        version="1.0",
        description="Regulatory gap test.",
    )

    db.add(framework)
    db.commit()
    db.refresh(framework)

    requirement = FrameworkControl(
        framework_id=framework.id,
        control_code="REQ-001",
        title="Access Management",
        description="Access management requirement.",
    )

    db.add(requirement)
    db.commit()
    db.refresh(requirement)

    result = (
        get_regulatory_requirement_intelligence(
            db,
            requirement,
            {1},
        )
    )

    assert result["state"] == "GAP"
    assert result["exposure"] == "CRITICAL"
    assert result["mapped_control_count"] == 0


def test_healthy_control_with_fresh_evidence_is_covered(
    db,
):

    framework = Framework(
        name="Coverage Framework",
        version="1.0",
        description="Coverage test.",
    )

    db.add(framework)
    db.commit()
    db.refresh(framework)

    requirement = FrameworkControl(
        framework_id=framework.id,
        control_code="REQ-002",
        title="Monitoring",
        description="Monitoring requirement.",
    )

    control = Control(
        title="Monitoring Control",
        description="Monitoring control.",
        control_type="Detective",
        status="Active",
        effectiveness=95,
        owner_id=1,
        created_by_id=1,
    )

    db.add_all(
        [
            requirement,
            control,
        ]
    )

    db.commit()

    db.refresh(requirement)
    db.refresh(control)

    db.add_all(
        [
            ControlFrameworkControl(
                control_id=control.id,
                framework_control_id=requirement.id,
            ),
            Evidence(
                control_id=control.id,
                title="Fresh Evidence",
                description="Fresh evidence.",
                file_name="evidence.pdf",
                file_path="/test/evidence.pdf",
                uploaded_by=1,
                uploaded_at=(
                    datetime.now(timezone.utc)
                    - timedelta(days=5)
                ),
            ),
        ]
    )

    db.commit()

    result = (
        get_regulatory_requirement_intelligence(
            db,
            requirement,
            {1},
        )
    )

    assert result["state"] == "COVERED"
    assert result["exposure"] == "LOW"
    assert result["mapped_control_count"] == 1


def test_weak_control_creates_partial_requirement(
    db,
):

    framework = Framework(
        name="Weak Control Framework",
        version="1.0",
        description="Weak control test.",
    )

    db.add(framework)
    db.commit()
    db.refresh(framework)

    requirement = FrameworkControl(
        framework_id=framework.id,
        control_code="REQ-003",
        title="Endpoint Protection",
        description="Endpoint protection requirement.",
    )

    control = Control(
        title="Weak Endpoint Control",
        description="Weak endpoint control.",
        control_type="Preventive",
        status="Active",
        effectiveness=55,
        owner_id=1,
        created_by_id=1,
    )

    db.add_all(
        [
            requirement,
            control,
        ]
    )

    db.commit()

    db.refresh(requirement)
    db.refresh(control)

    db.add(
        ControlFrameworkControl(
            control_id=control.id,
            framework_control_id=requirement.id,
        )
    )

    db.commit()

    result = (
        get_regulatory_requirement_intelligence(
            db,
            requirement,
            {1},
        )
    )

    assert result["state"] == "PARTIAL"
    assert result["exposure"] == "MEDIUM"


def test_high_risk_control_creates_high_exposure(
    db,
):

    framework = Framework(
        name="Risk Exposure Framework",
        version="1.0",
        description="Risk exposure test.",
    )

    db.add(framework)
    db.commit()
    db.refresh(framework)

    requirement = FrameworkControl(
        framework_id=framework.id,
        control_code="REQ-004",
        title="Risk Control",
        description="Risk-linked requirement.",
    )

    control = Control(
        title="Risk Control",
        description="Risk-linked control.",
        control_type="Preventive",
        status="Active",
        effectiveness=90,
        owner_id=1,
        created_by_id=1,
    )

    risk = Risk(
        title="High Risk",
        description="High risk.",
        likelihood=4,
        impact=4,
        risk_score=16,
        status="Open",
        owner_id=1,
        created_by_id=1,
    )

    db.add_all(
        [
            requirement,
            control,
            risk,
        ]
    )

    db.commit()

    db.refresh(requirement)
    db.refresh(control)
    db.refresh(risk)

    db.add_all(
        [
            ControlFrameworkControl(
                control_id=control.id,
                framework_control_id=requirement.id,
            ),
            RiskControl(
                control_id=control.id,
                risk_id=risk.id,
            ),
        ]
    )

    db.commit()

    result = (
        get_regulatory_requirement_intelligence(
            db,
            requirement,
            {1},
        )
    )

    assert result["exposure"] == "HIGH"


def test_framework_report_calculates_coverage(
    db,
):

    framework = Framework(
        name="Posture Framework",
        version="1.0",
        description="Posture test.",
    )

    db.add(framework)
    db.commit()
    db.refresh(framework)

    covered_requirement = FrameworkControl(
        framework_id=framework.id,
        control_code="REQ-001",
        title="Covered Requirement",
        description="Covered requirement.",
    )

    gap_requirement = FrameworkControl(
        framework_id=framework.id,
        control_code="REQ-002",
        title="Gap Requirement",
        description="Gap requirement.",
    )

    control = Control(
        title="Healthy Control",
        description="Healthy control.",
        control_type="Preventive",
        status="Active",
        effectiveness=95,
        owner_id=1,
        created_by_id=1,
    )

    db.add_all(
        [
            covered_requirement,
            gap_requirement,
            control,
        ]
    )

    db.commit()

    db.refresh(covered_requirement)
    db.refresh(gap_requirement)
    db.refresh(control)

    db.add_all(
        [
            ControlFrameworkControl(
                control_id=control.id,
                framework_control_id=(
                    covered_requirement.id
                ),
            ),
            Evidence(
                control_id=control.id,
                title="Fresh Evidence",
                description="Fresh evidence.",
                file_name="evidence.pdf",
                file_path="/test/evidence.pdf",
                uploaded_by=1,
                uploaded_at=(
                    datetime.now(timezone.utc)
                    - timedelta(days=5)
                ),
            ),
        ]
    )

    db.commit()

    report = (
        build_regulatory_intelligence_report(
            db,
            {1},
        )
    )

    assert report["framework_count"] == 1
    assert report["total_requirements"] == 2
    assert report["covered_requirements"] == 1
    assert report["gap_requirements"] == 1
    assert (
        report["overall_coverage_percent"]
        == 50.0
    )

    # An unmapped requirement is a critical
    # regulatory exposure.
    assert (
        report["overall_posture"]
        == "CRITICAL"
    )


def test_cross_framework_overlap_is_detected(
    db,
):

    framework_a = Framework(
        name="Framework A",
        version="1.0",
        description="First framework.",
    )

    framework_b = Framework(
        name="Framework B",
        version="1.0",
        description="Second framework.",
    )

    db.add_all(
        [
            framework_a,
            framework_b,
        ]
    )

    db.commit()

    db.refresh(framework_a)
    db.refresh(framework_b)

    requirement_a = FrameworkControl(
        framework_id=framework_a.id,
        control_code="A-001",
        title="Requirement A",
        description="Requirement A.",
    )

    requirement_b = FrameworkControl(
        framework_id=framework_b.id,
        control_code="B-001",
        title="Requirement B",
        description="Requirement B.",
    )

    control = Control(
        title="Shared Security Control",
        description="Shared control.",
        control_type="Preventive",
        status="Active",
        effectiveness=90,
        owner_id=1,
        created_by_id=1,
    )

    db.add_all(
        [
            requirement_a,
            requirement_b,
            control,
        ]
    )

    db.commit()

    db.refresh(requirement_a)
    db.refresh(requirement_b)
    db.refresh(control)

    db.add_all(
        [
            ControlFrameworkControl(
                control_id=control.id,
                framework_control_id=(
                    requirement_a.id
                ),
            ),
            ControlFrameworkControl(
                control_id=control.id,
                framework_control_id=(
                    requirement_b.id
                ),
            ),
        ]
    )

    db.commit()

    report = (
        build_regulatory_intelligence_report(
            db,
            {1},
        )
    )

    assert (
        report["overlapping_controls"]
        == 1
    )