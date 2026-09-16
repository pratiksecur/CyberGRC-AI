from datetime import date

import pytest

from app.models.framework import Framework
from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction
from app.services.dashboard_service import get_dashboard_data
from app.services.corrective_action_report_service import (
    get_corrective_action_report,
)


@pytest.fixture()
def corrective_action_data(db, users, resource_data):
    """Create actions that exercise both assignee and parent-audit scope."""

    framework = Framework(
        name="Phase 40 Test Framework",
        version="1.0",
        description="Framework used by Phase 40 authorization tests.",
    )
    db.add(framework)
    db.commit()
    db.refresh(framework)

    audit_manager = Audit(
        name="Manager Audit",
        framework_id=framework.id,
        auditor_id=users["manager"].id,
        created_by_id=users["manager"].id,
        scope="Manager audit scope",
        status="Planned",
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 30),
    )

    audit_admin = Audit(
        name="Admin Audit",
        framework_id=framework.id,
        auditor_id=users["admin"].id,
        created_by_id=users["admin"].id,
        scope="Admin audit scope",
        status="Planned",
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 30),
    )

    db.add_all([audit_manager, audit_admin])
    db.commit()
    db.refresh(audit_manager)
    db.refresh(audit_admin)

    finding_manager = AuditFinding(
        audit_id=audit_manager.id,
        control_id=resource_data["controls"]["analyst"].id,
        title="Manager Finding",
        description="Finding belonging to the manager audit.",
        severity="High",
        recommendation="Remediate the finding.",
        status="Open",
    )

    finding_admin = AuditFinding(
        audit_id=audit_admin.id,
        control_id=resource_data["controls"]["admin"].id,
        title="Admin Finding",
        description="Finding belonging to the admin audit.",
        severity="Critical",
        recommendation="Remediate the finding.",
        status="Open",
    )

    db.add_all([finding_manager, finding_admin])
    db.commit()
    db.refresh(finding_manager)
    db.refresh(finding_admin)

    action_manager_on_manager_audit = CorrectiveAction(
        finding_id=finding_manager.id,
        assigned_to=users["manager"].id,
        title="Manager Assigned Action",
        description="Visible to the manager.",
        priority="High",
        status="Open",
        due_date=date(2026, 10, 1),
    )

    action_admin_on_manager_audit = CorrectiveAction(
        finding_id=finding_manager.id,
        assigned_to=users["admin"].id,
        title="Admin Assigned Manager-Audit Action",
        description="Outside manager assignee scope.",
        priority="Critical",
        status="Open",
        due_date=date(2026, 10, 2),
    )

    action_manager_on_admin_audit = CorrectiveAction(
        finding_id=finding_admin.id,
        assigned_to=users["manager"].id,
        title="Manager Assigned Admin-Audit Action",
        description="Assignee is in scope, parent audit is not.",
        priority="Critical",
        status="Open",
        due_date=date(2026, 10, 3),
    )

    action_analyst_on_manager_audit = CorrectiveAction(
        finding_id=finding_manager.id,
        assigned_to=users["analyst"].id,
        title="Analyst Assigned Manager-Audit Action",
        description="Visible to the analyst only when parent audit is also in scope.",
        priority="Medium",
        status="Open",
        due_date=date(2026, 10, 4),
    )

    db.add_all(
        [
            action_manager_on_manager_audit,
            action_admin_on_manager_audit,
            action_manager_on_admin_audit,
            action_analyst_on_manager_audit,
        ]
    )
    db.commit()

    for action in [
        action_manager_on_manager_audit,
        action_admin_on_manager_audit,
        action_manager_on_admin_audit,
        action_analyst_on_manager_audit,
    ]:
        db.refresh(action)

    return {
        "manager_audit": audit_manager,
        "admin_audit": audit_admin,
        "manager_action": action_manager_on_manager_audit,
        "admin_action_on_manager_audit": action_admin_on_manager_audit,
        "manager_action_on_admin_audit": action_manager_on_admin_audit,
        "analyst_action": action_analyst_on_manager_audit,
    }


def test_manager_corrective_action_list_requires_assignee_and_parent_scope(
    client,
    users,
    auth_headers,
    corrective_action_data,
):
    response = client.get(
        "/api/v1/corrective-actions/",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    action_ids = {
        item["id"]
        for item in response.json()
    }

    assert corrective_action_data["manager_action"].id in action_ids

    assert (
        corrective_action_data[
            "admin_action_on_manager_audit"
        ].id
        not in action_ids
    )

    assert (
        corrective_action_data[
            "manager_action_on_admin_audit"
        ].id
        not in action_ids
    )


def test_analyst_corrective_action_list_is_own_scope(
    client,
    users,
    auth_headers,
    corrective_action_data,
):
    response = client.get(
        "/api/v1/corrective-actions/",
        headers=auth_headers(users["analyst"]),
    )

    assert response.status_code == 200

    action_ids = {
        item["id"]
        for item in response.json()
    }

    assert action_ids == {
        corrective_action_data["analyst_action"].id,
    }


def test_manager_cannot_get_out_of_scope_corrective_action(
    client,
    users,
    auth_headers,
    corrective_action_data,
):
    response = client.get(
        f"/api/v1/corrective-actions/"
        f"{corrective_action_data['admin_action_on_manager_audit'].id}",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 404


def test_manager_cannot_get_action_on_out_of_scope_parent_audit(
    client,
    users,
    auth_headers,
    corrective_action_data,
):
    response = client.get(
        f"/api/v1/corrective-actions/"
        f"{corrective_action_data['manager_action_on_admin_audit'].id}",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 404


def test_manager_corrective_action_report_is_scope_isolated(
    client,
    users,
    auth_headers,
    corrective_action_data,
):
    response = client.get(
        "/api/v1/reports/corrective-actions/",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    action_ids = {
        item["id"]
        for item in response.json()["actions"]
    }

    assert corrective_action_data["manager_action"].id in action_ids
    assert corrective_action_data["analyst_action"].id in action_ids
    assert corrective_action_data["admin_action_on_manager_audit"].id not in action_ids
    assert corrective_action_data["manager_action_on_admin_audit"].id not in action_ids


def test_dashboard_corrective_action_metrics_are_scope_isolated(
    db,
    users,
    resource_data,
    corrective_action_data,
):
    manager_dashboard = get_dashboard_data(
        db,
        users["manager"],
    )

    admin_dashboard = get_dashboard_data(
        db,
        users["admin"],
    )

    assert manager_dashboard["totalActions"] == 2
    assert admin_dashboard["totalActions"] == 4


def test_corrective_action_report_service_is_scope_isolated(
    db,
    users,
    corrective_action_data,
):
    manager_visible_ids = [
        users["manager"].id,
        users["analyst"].id,
        users["auditor"].id,
        users["employee"].id,
    ]

    report = get_corrective_action_report(
        db,
        manager_visible_ids,
    )

    action_ids = {
        item["id"]
        for item in report["actions"]
    }

    assert action_ids == {
        corrective_action_data["manager_action"].id,
        corrective_action_data["analyst_action"].id,
    }


def test_executive_ai_context_does_not_include_out_of_scope_actions(
    db,
    users,
    corrective_action_data,
    monkeypatch,
):
    from app.services.ai import (
        executive_dashboard_ai_service as service,
    )

    captured = {}

    class FakeProvider:
        def generate(self, prompt):
            captured["prompt"] = prompt

            return (
                '{"organization_risk_level":"Moderate",'
                '"executive_summary":"Scoped summary",'
                '"top_priorities":[],'
                '"recommended_next_steps":[]}'
            )

    monkeypatch.setattr(
        service,
        "get_ai_provider",
        lambda: FakeProvider(),
    )

    service.generate_executive_dashboard(
        db,
        users["manager"],
    )

    prompt = captured["prompt"]

    assert "Pending Corrective Actions:\n2" in prompt
    assert "Pending Corrective Actions:\n3" not in prompt
    assert "Pending Corrective Actions:\n4" not in prompt
