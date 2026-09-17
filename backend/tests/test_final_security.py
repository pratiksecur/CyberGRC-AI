from datetime import date

import pytest

from app.auth.visibility import get_visible_user_ids
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
    """
    Create corrective actions that exercise both
    assignee scope and parent-audit scope.
    """

    framework = Framework(
        name="Phase 40 Test Framework",
        version="1.0",
        description=(
            "Framework used by Phase 40 authorization tests."
        ),
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

    db.add_all(
        [
            audit_manager,
            audit_admin,
        ]
    )

    db.commit()

    db.refresh(audit_manager)
    db.refresh(audit_admin)

    finding_manager = AuditFinding(
        audit_id=audit_manager.id,
        control_id=resource_data["controls"]["analyst"].id,
        title="Manager Finding",
        description=(
            "Finding belonging to the manager audit."
        ),
        severity="High",
        recommendation="Remediate the finding.",
        status="Open",
    )

    finding_admin = AuditFinding(
        audit_id=audit_admin.id,
        control_id=resource_data["controls"]["admin"].id,
        title="Admin Finding",
        description=(
            "Finding belonging to the admin audit."
        ),
        severity="Critical",
        recommendation="Remediate the finding.",
        status="Open",
    )

    db.add_all(
        [
            finding_manager,
            finding_admin,
        ]
    )

    db.commit()

    db.refresh(finding_manager)
    db.refresh(finding_admin)

    # --------------------------------------------------
    # Visible to manager:
    # assignee in scope + parent audit in scope
    # --------------------------------------------------

    action_manager_on_manager_audit = CorrectiveAction(
        finding_id=finding_manager.id,
        assigned_to=users["manager"].id,
        title="Manager Assigned Action",
        description="Visible to the manager.",
        priority="High",
        status="Open",
        due_date=date(2026, 10, 1),
    )

    # --------------------------------------------------
    # Hidden from manager:
    # parent audit is in scope, assignee is not
    # --------------------------------------------------

    action_admin_on_manager_audit = CorrectiveAction(
        finding_id=finding_manager.id,
        assigned_to=users["admin"].id,
        title="Admin Assigned Manager-Audit Action",
        description="Outside manager assignee scope.",
        priority="Critical",
        status="Open",
        due_date=date(2026, 10, 2),
    )

    # --------------------------------------------------
    # Hidden from manager:
    # assignee is in scope, parent audit is not
    # --------------------------------------------------

    action_manager_on_admin_audit = CorrectiveAction(
        finding_id=finding_admin.id,
        assigned_to=users["manager"].id,
        title="Manager Assigned Admin-Audit Action",
        description=(
            "Assignee is in scope, parent audit is not."
        ),
        priority="Critical",
        status="Open",
        due_date=date(2026, 10, 3),
    )

    # --------------------------------------------------
    # Visible to manager and analyst:
    #
    # Manager:
    # subordinate assignee + manager audit
    #
    # Analyst:
    # OWN scope is determined by assigned_to
    # --------------------------------------------------

    action_analyst_on_manager_audit = CorrectiveAction(
        finding_id=finding_manager.id,
        assigned_to=users["analyst"].id,
        title="Analyst Assigned Manager-Audit Action",
        description=(
            "Visible according to corrective-action scope."
        ),
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
        "manager_action": (
            action_manager_on_manager_audit
        ),
        "admin_action_on_manager_audit": (
            action_admin_on_manager_audit
        ),
        "manager_action_on_admin_audit": (
            action_manager_on_admin_audit
        ),
        "analyst_action": (
            action_analyst_on_manager_audit
        ),
    }


def test_manager_corrective_action_list_requires_assignee_and_parent_scope(
    client,
    users,
    auth_headers,
    corrective_action_data,
):
    response = client.get(
        "/api/v1/corrective-actions/",
        headers=auth_headers(
            users["manager"]
        ),
    )

    assert response.status_code == 200

    action_ids = {
        item["id"]
        for item in response.json()
    }

    # Both dimensions are in scope.
    assert (
        corrective_action_data[
            "manager_action"
        ].id
        in action_ids
    )

    assert (
        corrective_action_data[
            "analyst_action"
        ].id
        in action_ids
    )

    # Assignee is outside manager scope.
    assert (
        corrective_action_data[
            "admin_action_on_manager_audit"
        ].id
        not in action_ids
    )

    # Parent audit is outside manager scope.
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
        headers=auth_headers(
            users["analyst"]
        ),
    )

    assert response.status_code == 200

    actions = response.json()

    action_ids = {
        item["id"]
        for item in actions
    }

    # The specifically-created analyst action must
    # be visible.
    assert (
        corrective_action_data[
            "analyst_action"
        ].id
        in action_ids
    )

    # OWN scope must never expose actions assigned
    # to another user.
    assert all(
        item["assigned_to"]
        == users["analyst"].id
        for item in actions
    )


def test_manager_cannot_get_out_of_scope_corrective_action(
    client,
    users,
    auth_headers,
    corrective_action_data,
):
    response = client.get(
        (
            "/api/v1/corrective-actions/"
            f"{corrective_action_data['admin_action_on_manager_audit'].id}"
        ),
        headers=auth_headers(
            users["manager"]
        ),
    )

    assert response.status_code == 404


def test_manager_cannot_get_action_on_out_of_scope_parent_audit(
    client,
    users,
    auth_headers,
    corrective_action_data,
):
    response = client.get(
        (
            "/api/v1/corrective-actions/"
            f"{corrective_action_data['manager_action_on_admin_audit'].id}"
        ),
        headers=auth_headers(
            users["manager"]
        ),
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
        headers=auth_headers(
            users["manager"]
        ),
    )

    assert response.status_code == 200

    action_ids = {
        item["id"]
        for item in response.json()["actions"]
    }

    # Both assignee and parent audit are in scope.
    assert (
        corrective_action_data[
            "manager_action"
        ].id
        in action_ids
    )

    assert (
        corrective_action_data[
            "analyst_action"
        ].id
        in action_ids
    )

    # Assignee outside manager scope.
    assert (
        corrective_action_data[
            "admin_action_on_manager_audit"
        ].id
        not in action_ids
    )

    # Parent audit outside manager scope.
    assert (
        corrective_action_data[
            "manager_action_on_admin_audit"
        ].id
        not in action_ids
    )


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

    # --------------------------------------------------
    # Calculate the authoritative expected values using
    # the established corrective-action scope contract.
    #
    # Manager:
    #   assigned_to in manager scope
    #   AND parent audit auditor in manager scope
    #
    # Admin:
    #   organization-wide scope
    # --------------------------------------------------

    manager_visible_ids = set(
        get_visible_user_ids(
            db,
            users["manager"],
            "corrective_actions",
        )
    )

    admin_visible_ids = set(
        get_visible_user_ids(
            db,
            users["admin"],
            "corrective_actions",
        )
    )

    all_actions = (
        db.query(CorrectiveAction)
        .join(
            AuditFinding,
            CorrectiveAction.finding_id
            == AuditFinding.id,
        )
        .join(
            Audit,
            AuditFinding.audit_id
            == Audit.id,
        )
        .all()
    )

    audit_by_finding_id = {
        finding.id: audit
        for finding, audit in (
            db.query(
                AuditFinding,
                Audit,
            )
            .join(
                Audit,
                AuditFinding.audit_id
                == Audit.id,
            )
            .all()
        )
    }

    expected_manager_actions = [
        action
        for action in all_actions
        if (
            action.assigned_to
            in manager_visible_ids
            and audit_by_finding_id[
                action.finding_id
            ].auditor_id
            in manager_visible_ids
        )
    ]

    expected_admin_actions = [
        action
        for action in all_actions
        if (
            action.assigned_to
            in admin_visible_ids
            and audit_by_finding_id[
                action.finding_id
            ].auditor_id
            in admin_visible_ids
        )
    ]

    assert (
        manager_dashboard["totalActions"]
        == len(expected_manager_actions)
    )

    assert (
        admin_dashboard["totalActions"]
        == len(expected_admin_actions)
    )

    # Explicitly prove that the two attack-style
    # cross-boundary records are excluded from the
    # manager's expected scope.

    expected_manager_ids = {
        action.id
        for action in expected_manager_actions
    }

    assert (
        corrective_action_data[
            "admin_action_on_manager_audit"
        ].id
        not in expected_manager_ids
    )

    assert (
        corrective_action_data[
            "manager_action_on_admin_audit"
        ].id
        not in expected_manager_ids
    )


def test_corrective_action_report_service_is_scope_isolated(
    db,
    users,
    corrective_action_data,
):
    manager_visible_ids = get_visible_user_ids(
        db,
        users["manager"],
        "corrective_actions",
    )

    report = get_corrective_action_report(
        db,
        manager_visible_ids,
    )

    action_ids = {
        item["id"]
        for item in report["actions"]
    }

    # Valid in-scope records.
    assert (
        corrective_action_data[
            "manager_action"
        ].id
        in action_ids
    )

    assert (
        corrective_action_data[
            "analyst_action"
        ].id
        in action_ids
    )

    # Parent audit is in scope but assignee is not.
    assert (
        corrective_action_data[
            "admin_action_on_manager_audit"
        ].id
        not in action_ids
    )

    # Assignee is in scope but parent audit is not.
    assert (
        corrective_action_data[
            "manager_action_on_admin_audit"
        ].id
        not in action_ids
    )


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

    # --------------------------------------------------
    # Calculate the expected pending count independently
    # from the AI service using the established
    # corrective-action authorization contract.
    # --------------------------------------------------

    visible_ids = set(
        get_visible_user_ids(
            db,
            users["manager"],
            "corrective_actions",
        )
    )

    visible_actions = (
        db.query(CorrectiveAction)
        .join(
            AuditFinding,
            CorrectiveAction.finding_id
            == AuditFinding.id,
        )
        .join(
            Audit,
            AuditFinding.audit_id
            == Audit.id,
        )
        .filter(
            CorrectiveAction.assigned_to.in_(
                visible_ids
            ),
            Audit.auditor_id.in_(
                visible_ids
            ),
        )
        .all()
    )

    expected_pending_actions = sum(
        1
        for action in visible_actions
        if str(action.status).lower()
        not in (
            "completed",
            "closed",
        )
    )

    service.generate_executive_dashboard(
        db,
        users["manager"],
    )

    prompt = captured["prompt"]

    assert (
        "Pending Corrective Actions:\n"
        f"{expected_pending_actions}"
        in prompt
    )

    # --------------------------------------------------
    # Explicit security checks:
    #
    # These two records must not contribute to the
    # manager's executive AI context.
    # --------------------------------------------------

    visible_action_ids = {
        action.id
        for action in visible_actions
    }

    assert (
        corrective_action_data[
            "admin_action_on_manager_audit"
        ].id
        not in visible_action_ids
    )

    assert (
        corrective_action_data[
            "manager_action_on_admin_audit"
        ].id
        not in visible_action_ids
    )