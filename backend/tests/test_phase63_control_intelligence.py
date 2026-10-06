from datetime import datetime, timedelta, timezone

from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.control import Control
from app.models.control_framework_control import (
    ControlFrameworkControl,
)
from app.models.framework import Framework
from app.models.framework_control import FrameworkControl
from app.models.risk import Risk
from app.models.risk_control import RiskControl

from app.services.control_intelligence_service import (
    build_control_intelligence_report,
    get_control_intelligence,
)


def test_control_intelligence_returns_control_data(
    db,
    users,
    resource_data,
):
    control = resource_data[
        "controls"
    ]["admin"]

    report = build_control_intelligence_report(
        db,
        {
            users["admin"].id,
        },
    )

    assert report["summary"][
        "total_controls"
    ] == 1

    item = next(
        item
        for item in report["controls"]
        if item["control_id"] == control.id
    )

    assert item["effectiveness"] == 90
    assert item["evidence_count"] == 1

    # The base fixture does not create a
    # RiskControl mapping.
    assert item["risk_count"] == 0


def test_control_intelligence_respects_visibility_scope(
    db,
    users,
    resource_data,
):
    report = build_control_intelligence_report(
        db,
        {
            users["manager"].id,
            users["analyst"].id,
            users["auditor"].id,
            users["employee"].id,
        },
    )

    admin_control = resource_data[
        "controls"
    ]["admin"]

    assert report["summary"][
        "total_controls"
    ] == 4

    assert all(
        item["control_id"]
        != admin_control.id
        for item in report["controls"]
    )


def test_missing_evidence_is_detected(
    db,
    users,
):
    control = Control(
        title="No Evidence Control",
        description="Control without supporting evidence.",
        control_type="Preventive",
        status="Active",
        effectiveness=80,
        owner_id=users["admin"].id,
        created_by_id=users["admin"].id,
    )

    db.add(control)
    db.commit()
    db.refresh(control)

    result = get_control_intelligence(
        db,
        control,
        {users["admin"].id},
    )

    assert result["evidence_count"] == 0
    assert result["evidence_state"] == "MISSING"

    assert "MISSING_EVIDENCE" in (
        result["monitoring_signals"]
    )


def test_low_effectiveness_is_detected(
    db,
    users,
):
    control = Control(
        title="Weak Control",
        description="Control with low effectiveness.",
        control_type="Detective",
        status="Active",
        effectiveness=40,
        owner_id=users["admin"].id,
        created_by_id=users["admin"].id,
    )

    db.add(control)
    db.commit()
    db.refresh(control)

    result = get_control_intelligence(
        db,
        control,
        {users["admin"].id},
    )

    assert result["health_state"] == "CRITICAL"

    assert (
        result["effectiveness_trend_signal"]
        == "DEGRADING"
    )

    assert "LOW_EFFECTIVENESS" in (
        result["monitoring_signals"]
    )


def test_risk_mapping_is_detected(
    db,
    users,
):
    risk = Risk(
        title="Critical Risk",
        description="Critical risk for control intelligence.",
        likelihood=5,
        impact=5,
        risk_score=25,
        status="Open",
        owner_id=users["admin"].id,
        created_by_id=users["admin"].id,
    )

    control = Control(
        title="Risk Control",
        description="Control mapped to a critical risk.",
        control_type="Preventive",
        status="Active",
        effectiveness=90,
        owner_id=users["admin"].id,
        created_by_id=users["admin"].id,
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

    mapping = RiskControl(
        risk_id=risk.id,
        control_id=control.id,
    )

    db.add(mapping)
    db.commit()

    result = get_control_intelligence(
        db,
        control,
        {users["admin"].id},
    )

    assert result["risk_count"] == 1
    assert result["critical_risk_count"] == 1

    assert "CRITICAL_RISK_EXPOSURE" in (
        result["monitoring_signals"]
    )


def test_framework_mapping_is_detected(
    db,
    users,
):
    framework = Framework(
        name="Phase 63 Test Framework",
        version="1.0",
        description="Framework for Phase 63 testing.",
    )

    db.add(framework)
    db.commit()
    db.refresh(framework)

    framework_control = FrameworkControl(
        framework_id=framework.id,
        control_code="P63-001",
        title="Phase 63 Framework Requirement",
        description="Requirement mapped to a control.",
    )

    db.add(framework_control)
    db.commit()
    db.refresh(framework_control)

    control = Control(
        title="Framework Control",
        description="Control mapped to a framework.",
        control_type="Preventive",
        status="Active",
        effectiveness=90,
        owner_id=users["admin"].id,
        created_by_id=users["admin"].id,
    )

    db.add(control)
    db.commit()
    db.refresh(control)

    mapping = ControlFrameworkControl(
        control_id=control.id,
        framework_control_id=framework_control.id,
    )

    db.add(mapping)
    db.commit()

    result = get_control_intelligence(
        db,
        control,
        {users["admin"].id},
    )

    assert result["framework_count"] == 1

    assert framework.name in (
        result["framework_names"]
    )


def test_open_critical_finding_degrades_control(
    db,
    users,
    resource_data,
):
    control = resource_data[
        "controls"
    ]["admin"]

    framework = Framework(
        name="Finding Test Framework",
        version="1.0",
        description="Framework for finding test.",
    )

    db.add(framework)
    db.commit()
    db.refresh(framework)

    audit = Audit(
        name="Control Intelligence Audit",
        framework_id=framework.id,
        auditor_id=users["admin"].id,
        created_by_id=users["admin"].id,
        scope="Control",
        status="In Progress",
        start_date=datetime.now().date(),
        end_date=(
            datetime.now().date()
            + timedelta(days=30)
        ),
    )

    db.add(audit)
    db.commit()
    db.refresh(audit)

    finding = AuditFinding(
        audit_id=audit.id,
        control_id=control.id,
        title="Critical Control Finding",
        description="Critical control weakness.",
        severity="Critical",
        recommendation="Remediate immediately.",
        status="Open",
    )

    db.add(finding)
    db.commit()

    result = get_control_intelligence(
        db,
        control,
        {users["admin"].id},
    )

    assert result[
        "critical_finding_count"
    ] == 1

    assert "CRITICAL_CONTROL_FINDING" in (
        result["monitoring_signals"]
    )

    assert result["health_state"] == "CRITICAL"


def test_report_calculates_coverage(
    db,
    users,
    resource_data,
):
    report = build_control_intelligence_report(
        db,
        {users["admin"].id},
    )

    summary = report["summary"]

    assert summary[
        "total_controls"
    ] == 1

    assert summary[
        "evidence_coverage_percent"
    ] == 100

    # The base fixture has evidence for the
    # admin control but no RiskControl mapping.
    assert summary[
        "risk_coverage_percent"
    ] == 0


def test_report_calculates_average_effectiveness(
    db,
    users,
    resource_data,
):
    report = build_control_intelligence_report(
        db,
        {
            users["admin"].id,
            users["manager"].id,
            users["analyst"].id,
        },
    )

    assert report["summary"][
        "average_effectiveness"
    ] == 85


def test_control_intelligence_api(
    client,
    users,
    resource_data,
    auth_headers,
):
    response = client.get(
        "/api/v1/controls/intelligence",
        headers=auth_headers(
            users["admin"]
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert "generated_at" in body
    assert "summary" in body
    assert "controls" in body

    assert body["summary"][
        "total_controls"
    ] == 5


def test_control_intelligence_respects_employee_visibility(
    client,
    users,
    resource_data,
    auth_headers,
):
    response = client.get(
        "/api/v1/controls/intelligence",
        headers=auth_headers(
            users["employee"]
        ),
    )

    assert response.status_code == 200

    body = response.json()

    # Employee has controls:view with
    # ORGANIZATION visibility.
    assert body["summary"][
        "total_controls"
    ] == 5

    control_ids = {
        item["control_id"]
        for item in body["controls"]
    }

    expected_ids = {
        control.id
        for control in resource_data[
            "controls"
        ].values()
    }

    assert control_ids == expected_ids