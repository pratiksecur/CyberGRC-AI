from datetime import date, timedelta

from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.control import Control
from app.models.corrective_action import CorrectiveAction

from app.services.audit_assurance_service import (
    build_audit_assurance,
)


def test_audit_assurance_returns_core_sections(
    db,
    users,
):
    admin = users["admin"]

    result = build_audit_assurance(
        db,
        admin,
    )

    assert "portfolio" in result
    assert "planning" in result
    assert "testing" in result
    assert "evidence" in result
    assert "remediation" in result
    assert "closure" in result
    assert "assurance_signals" in result
    assert "audits" in result
    assert "scope" in result
    assert "generated_at" in result


def test_audit_assurance_admin_sees_organization_audits(
    db,
    users,
    resource_data,
):
    admin = users["admin"]

    result = build_audit_assurance(
        db,
        admin,
    )

    audit_ids = {
        audit["id"]
        for audit in result["audits"]
    }

    admin_audit = resource_data[
        "audits"
    ]["admin"]

    manager_audit = resource_data[
        "audits"
    ]["manager"]

    assert admin_audit.id in audit_ids
    assert manager_audit.id in audit_ids


def test_audit_assurance_manager_is_scope_aware(
    db,
    users,
    resource_data,
):
    manager = users["manager"]

    result = build_audit_assurance(
        db,
        manager,
    )

    audit_ids = {
        audit["id"]
        for audit in result["audits"]
    }

    manager_audit = resource_data[
        "audits"
    ]["manager"]

    admin_audit = resource_data[
        "audits"
    ]["admin"]

    assert manager_audit.id in audit_ids

    assert (
        admin_audit.id
        not in audit_ids
    )


def test_audit_assurance_employee_has_organization_audit_visibility(
    db,
    users,
    resource_data,
):
    employee = users["employee"]

    result = build_audit_assurance(
        db,
        employee,
    )

    audit_ids = {
        audit["id"]
        for audit in result["audits"]
    }

    expected_audit_ids = {
        audit.id
        for audit in resource_data[
            "audits"
        ].values()
    }

    assert audit_ids == expected_audit_ids

    assert (
        result[
            "scope"
        ]["audit_count"]
        == len(expected_audit_ids)
    )


def test_audit_assurance_detects_overdue_audit(
    db,
    users,
    resource_data,
):
    admin = users["admin"]

    audit = resource_data[
        "audits"
    ]["admin"]

    audit.status = "In Progress"

    audit.end_date = (
        date.today()
        - timedelta(days=2)
    )

    db.commit()

    result = build_audit_assurance(
        db,
        admin,
    )

    assert (
        result[
            "portfolio"
        ]["overdue"]
        >= 1
    )

    assert any(
        signal["signal"]
        == "OVERDUE_AUDITS"
        for signal
        in result[
            "assurance_signals"
        ]
    )


def test_audit_assurance_detects_critical_finding(
    db,
    users,
    resource_data,
):
    admin = users["admin"]

    audit = resource_data[
        "audits"
    ]["admin"]

    control = resource_data[
        "controls"
    ]["admin"]

    finding = AuditFinding(
        audit_id=audit.id,
        control_id=control.id,
        title="Phase 68 Critical Finding",
        description=(
            "Critical audit assurance finding."
        ),
        severity="Critical",
        recommendation=(
            "Remediation required."
        ),
        status="Open",
    )

    db.add(finding)
    db.commit()

    result = build_audit_assurance(
        db,
        admin,
    )

    assert (
        result[
            "testing"
        ]["critical_findings"]
        >= 1
    )

    assert any(
        signal["signal"]
        == "CRITICAL_FINDINGS"
        for signal
        in result[
            "assurance_signals"
        ]
    )


def test_audit_assurance_detects_open_finding(
    db,
    users,
    resource_data,
):
    admin = users["admin"]

    audit = resource_data[
        "audits"
    ]["admin"]

    control = resource_data[
        "controls"
    ]["admin"]

    finding = AuditFinding(
        audit_id=audit.id,
        control_id=control.id,
        title="Phase 68 Open Finding",
        description=(
            "Open audit finding."
        ),
        severity="High",
        recommendation=(
            "Remediate the finding."
        ),
        status="Open",
    )

    db.add(finding)
    db.commit()

    result = build_audit_assurance(
        db,
        admin,
    )

    assert (
        result[
            "testing"
        ]["open_findings"]
        >= 1
    )


def test_audit_assurance_detects_overdue_corrective_action(
    db,
    users,
    resource_data,
):
    admin = users["admin"]

    audit = resource_data[
        "audits"
    ]["admin"]

    control = resource_data[
        "controls"
    ]["admin"]

    finding = AuditFinding(
        audit_id=audit.id,
        control_id=control.id,
        title="Phase 68 Remediation Finding",
        description=(
            "Finding requiring remediation."
        ),
        severity="High",
        recommendation=(
            "Implement corrective action."
        ),
        status="Open",
    )

    db.add(finding)
    db.commit()
    db.refresh(finding)

    action = CorrectiveAction(
        finding_id=finding.id,
        assigned_to=admin.id,
        title="Phase 68 Overdue Action",
        description=(
            "Corrective action for the audit finding."
        ),
        priority="High",
        status="In Progress",
        due_date=(
            date.today()
            - timedelta(days=2)
        ),
    )

    db.add(action)
    db.commit()

    result = build_audit_assurance(
        db,
        admin,
    )

    assert (
        result[
            "remediation"
        ]["overdue_actions"]
        >= 1
    )

    assert any(
        signal["signal"]
        == "OVERDUE_CORRECTIVE_ACTIONS"
        for signal
        in result[
            "assurance_signals"
        ]
    )


def test_audit_assurance_detects_evidence_coverage(
    db,
    users,
    resource_data,
):
    admin = users["admin"]

    audit = resource_data[
        "audits"
    ]["admin"]

    control = resource_data[
        "controls"
    ]["admin"]

    finding = AuditFinding(
        audit_id=audit.id,
        control_id=control.id,
        title="Phase 68 Evidence Finding",
        description=(
            "Finding used to test evidence coverage."
        ),
        severity="Medium",
        recommendation=(
            "Review supporting evidence."
        ),
        status="Open",
    )

    db.add(finding)
    db.commit()

    result = build_audit_assurance(
        db,
        admin,
    )

    assert (
        result[
            "evidence"
        ]["controls_referenced"]
        >= 1
    )


def test_audit_assurance_detects_planning_gap(
    db,
    users,
    resource_data,
):
    admin = users["admin"]

    audit = resource_data[
        "audits"
    ]["admin"]

    audit.scope = ""

    db.commit()

    result = build_audit_assurance(
        db,
        admin,
    )

    audit_result = next(
        item
        for item in result["audits"]
        if item["id"] == audit.id
    )

    assert (
        audit_result[
            "planning_complete"
        ]
        is False
    )

    assert (
        "PLANNING_INCOMPLETE"
        in audit_result[
            "closure_blockers"
        ]
    )


def test_audit_assurance_detects_closure_readiness(
    db,
    users,
    resource_data,
):
    admin = users["admin"]

    existing_audit = resource_data[
        "audits"
    ]["admin"]

    clean_audit = Audit(
        name="Phase 68 Closure Ready Audit",
        framework_id=existing_audit.framework_id,
        auditor_id=admin.id,
        created_by_id=admin.id,
        scope="Phase 68 Assurance Validation",
        status="In Progress",
        start_date=date.today(),
        end_date=(
            date.today()
            + timedelta(days=10)
        ),
    )

    db.add(
        clean_audit
    )

    db.commit()

    db.refresh(
        clean_audit
    )

    result = build_audit_assurance(
        db,
        admin,
    )

    audit_result = next(
        item
        for item in result["audits"]
        if item["id"]
        == clean_audit.id
    )

    assert (
        audit_result[
            "planning_complete"
        ]
        is True
    )

    assert (
        audit_result[
            "finding_count"
        ]
        == 0
    )

    assert (
        audit_result[
            "open_findings"
        ]
        == 0
    )

    assert (
        audit_result[
            "open_corrective_actions"
        ]
        == 0
    )

    assert (
        audit_result[
            "closure_ready"
        ]
        is True
    )

    assert (
        audit_result[
            "closure_blockers"
        ]
        == []
    )

    assert (
        result[
            "closure"
        ]["ready"]
        >= 1
    )

def test_audit_assurance_is_read_only(
    db,
    users,
):
    admin = users["admin"]

    before_audits = db.query(
        Audit
    ).count()

    before_findings = db.query(
        AuditFinding
    ).count()

    before_controls = db.query(
        Control
    ).count()

    before_actions = db.query(
        CorrectiveAction
    ).count()

    result = build_audit_assurance(
        db,
        admin,
    )

    assert result is not None

    assert (
        db.query(Audit).count()
        == before_audits
    )

    assert (
        db.query(AuditFinding).count()
        == before_findings
    )

    assert (
        db.query(Control).count()
        == before_controls
    )

    assert (
        db.query(
            CorrectiveAction
        ).count()
        == before_actions
    )

def test_open_finding_blocks_audit_closure(
    db,
    users,
    resource_data,
):
    admin = users["admin"]

    audit = resource_data[
        "audits"
    ]["admin"]

    audit.status = "In Progress"
    audit.start_date = date.today()
    audit.end_date = (
        date.today()
        + timedelta(days=10)
    )

    db.commit()

    result = build_audit_assurance(
        db,
        admin,
    )

    audit_result = next(
        item
        for item in result["audits"]
        if item["id"]
        == audit.id
    )

    assert (
        audit_result[
            "open_findings"
        ]
        >= 1
    )

    assert (
        audit_result[
            "closure_ready"
        ]
        is False
    )

    assert (
        "OPEN_FINDINGS"
        in audit_result[
            "closure_blockers"
        ]
    )