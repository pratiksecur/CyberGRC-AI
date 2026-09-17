from datetime import date, timedelta

from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction
from app.models.control_framework_control import (
    ControlFrameworkControl,
)
from app.models.framework_control import FrameworkControl
from app.models.risk_control import RiskControl


# ==========================================================
# HELPERS
# ==========================================================

def _headers(
    auth_headers,
    user,
):
    return auth_headers(user)


# ==========================================================
# FULL GRC INTELLIGENCE CHAIN
# ==========================================================

def test_phase45_risk_intelligence_builds_full_grc_chain(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    manager = users["manager"]

    risk = resource_data["risks"]["manager"]

    control = resource_data["controls"]["manager"]

    audit = resource_data["audits"]["manager"]

    existing_finding = (
        resource_data["findings"]["manager"]
    )

    existing_action = (
        resource_data[
            "corrective_actions"
        ]["manager"]
    )

    # ------------------------------------------------------
    # FRAMEWORK CONTROL
    # ------------------------------------------------------

    framework_control = FrameworkControl(
        framework_id=1,
        control_code="GRC-01",
        title="Manager Governance Control",
        description=(
            "Control used by the intelligence test."
        ),
    )

    db.add(framework_control)

    db.commit()

    db.refresh(framework_control)

    # ------------------------------------------------------
    # CONTROL -> FRAMEWORK
    # ------------------------------------------------------

    db.add(
        ControlFrameworkControl(
            control_id=control.id,
            framework_control_id=(
                framework_control.id
            ),
        )
    )

    # ------------------------------------------------------
    # RISK -> CONTROL
    # ------------------------------------------------------

    db.add(
        RiskControl(
            risk_id=risk.id,
            control_id=control.id,
        )
    )

    db.commit()

    # ------------------------------------------------------
    # NEW AUDIT FINDING
    # ------------------------------------------------------

    finding = AuditFinding(
        audit_id=audit.id,
        control_id=control.id,
        title="Manager Control Finding",
        description=(
            "Test finding for intelligence aggregation."
        ),
        severity="Critical",
        recommendation=(
            "Remediate the control gap."
        ),
        status="Open",
    )

    db.add(finding)

    db.commit()

    db.refresh(finding)

    # ------------------------------------------------------
    # NEW CORRECTIVE ACTION
    # ------------------------------------------------------

    action = CorrectiveAction(
        finding_id=finding.id,
        assigned_to=manager.id,
        title="Remediate Manager Finding",
        description="Test corrective action.",
        priority="High",
        status="Open",
        due_date=(
            date.today()
            - timedelta(days=2)
        ),
    )

    db.add(action)

    db.commit()

    db.refresh(action)

    # ------------------------------------------------------
    # API REQUEST
    # ------------------------------------------------------

    response = client.get(
        f"/api/v1/intelligence/risk/{risk.id}",
        headers=_headers(
            auth_headers,
            manager,
        ),
    )

    assert response.status_code == 200

    body = response.json()

    # ------------------------------------------------------
    # RISK
    # ------------------------------------------------------

    assert body["risk_id"] == risk.id

    assert body["risk_title"] == risk.title

    assert body["risk_score"] == risk.risk_score

    # ------------------------------------------------------
    # CONTROL METRICS
    # ------------------------------------------------------

    assert (
        body["metrics"]["control_count"]
        == 1
    )

    assert (
        body["metrics"]["controls_with_evidence"]
        == 1
    )

    assert (
        body["metrics"]["evidence_coverage_percent"]
        == 100.0
    )

    assert (
        body["metrics"][
            "average_control_effectiveness"
        ]
        == 85.0
    )

    # ------------------------------------------------------
    # FRAMEWORK
    # ------------------------------------------------------

    assert (
        body["metrics"]["framework_count"]
        == 1
    )

    # ------------------------------------------------------
    # FINDINGS
    # ------------------------------------------------------

    # The fixture already contains one manager finding.
    # This test adds another one.

    assert (
        body["metrics"]["finding_count"]
        == 2
    )

    assert (
        body["metrics"]["open_findings"]
        == 2
    )

    # Existing finding = Medium
    # New finding = Critical

    assert (
        body["metrics"]["critical_findings"]
        == 1
    )

    # ------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------

    # The fixture already contains one manager action.
    # This test adds another one.

    assert (
        body["metrics"]["action_count"]
        == 2
    )

    # Existing action = Pending
    # New action = Open

    assert (
        body["metrics"]["open_actions"]
        == 2
    )

    # Only the newly-created action is overdue.

    assert (
        body["metrics"]["overdue_actions"]
        == 1
    )

    assert (
        body["metrics"][
            "remediation_completion_percent"
        ]
        == 0.0
    )

    # ------------------------------------------------------
    # RESIDUAL RISK
    # ------------------------------------------------------

    # Risk score = 12
    # Control effectiveness = 85%
    #
    # 12 * (1 - 0.85) = 1.8

    assert (
        body["metrics"][
            "estimated_residual_risk"
        ]
        == 1.8
    )

    # ------------------------------------------------------
    # NESTED GRAPH
    # ------------------------------------------------------

    intelligence_control = (
        body["controls"][0]
    )

    assert (
        intelligence_control["id"]
        == control.id
    )

    # ------------------------------------------------------
    # EVIDENCE
    # ------------------------------------------------------

    assert (
        len(
            intelligence_control[
                "evidence"
            ]
        )
        == 1
    )

    assert (
        intelligence_control[
            "evidence"
        ][0]["id"]
        == resource_data[
            "evidence"
        ]["manager"].id
    )

    # ------------------------------------------------------
    # FRAMEWORK
    # ------------------------------------------------------

    assert (
        intelligence_control[
            "frameworks"
        ][0]["control_code"]
        == "GRC-01"
    )

    # ------------------------------------------------------
    # FINDINGS
    # ------------------------------------------------------

    finding_ids = {
        item["id"]
        for item in intelligence_control[
            "findings"
        ]
    }

    assert (
        existing_finding.id
        in finding_ids
    )

    assert (
        finding.id
        in finding_ids
    )

    # ------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------

    action_ids = {
        action_item["id"]
        for finding_item in intelligence_control[
            "findings"
        ]
        for action_item in finding_item[
            "actions"
        ]
    }

    assert (
        existing_action.id
        in action_ids
    )

    assert (
        action.id
        in action_ids
    )

    # Find the newly-created action.

    new_action_payload = next(
        action_item
        for finding_item in intelligence_control[
            "findings"
        ]
        for action_item in finding_item[
            "actions"
        ]
        if action_item["id"] == action.id
    )

    assert (
        new_action_payload["overdue"]
        is True
    )


# ==========================================================
# RISK VISIBILITY
# ==========================================================

def test_phase45_respects_risk_visibility(
    client,
    users,
    resource_data,
    auth_headers,
):
    admin = users["admin"]

    admin_risk = (
        resource_data["risks"]["admin"]
    )

    # ------------------------------------------------------
    # EMPLOYEE CANNOT SEE ADMIN RISK
    # ------------------------------------------------------

    response = client.get(
        f"/api/v1/intelligence/risk/{admin_risk.id}",
        headers=_headers(
            auth_headers,
            users["employee"],
        ),
    )

    assert response.status_code == 404

    # ------------------------------------------------------
    # ADMIN CAN SEE ADMIN RISK
    # ------------------------------------------------------

    response = client.get(
        f"/api/v1/intelligence/risk/{admin_risk.id}",
        headers=_headers(
            auth_headers,
            admin,
        ),
    )

    assert response.status_code == 200


# ==========================================================
# DOWNSTREAM AUDIT SCOPE
# ==========================================================

def test_phase45_filters_downstream_audit_data_by_audit_scope(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    analyst = users["analyst"]

    risk = resource_data["risks"]["analyst"]

    control = resource_data["controls"]["analyst"]

    existing_finding = (
        resource_data[
            "findings"
        ]["analyst"]
    )

    manager_audit = (
        resource_data[
            "audits"
        ]["manager"]
    )

    # ------------------------------------------------------
    # RISK -> CONTROL
    # ------------------------------------------------------

    db.add(
        RiskControl(
            risk_id=risk.id,
            control_id=control.id,
        )
    )

    db.commit()

    # ------------------------------------------------------
    # HIDDEN MANAGER-AUDIT FINDING
    # ------------------------------------------------------

    hidden_finding = AuditFinding(
        audit_id=manager_audit.id,
        control_id=control.id,
        title="Hidden Manager Audit Finding",
        description=(
            "Must be filtered from analyst intelligence."
        ),
        severity="Critical",
        recommendation="Hidden remediation.",
        status="Open",
    )

    db.add(hidden_finding)

    db.commit()

    # ------------------------------------------------------
    # REQUEST AS ANALYST
    # ------------------------------------------------------

    response = client.get(
        f"/api/v1/intelligence/risk/{risk.id}",
        headers=_headers(
            auth_headers,
            analyst,
        ),
    )

    assert response.status_code == 200

    body = response.json()

    # ------------------------------------------------------
    # CONTROL
    # ------------------------------------------------------

    assert (
        body["metrics"]["control_count"]
        == 1
    )

    # ------------------------------------------------------
    # EXISTING ANALYST FINDING
    # ------------------------------------------------------

    # The fixture already contains the analyst's own
    # audit finding. It is visible because analyst audit
    # scope is OWN.

    assert (
        body["metrics"]["finding_count"]
        == 1
    )

    assert (
        body["metrics"]["open_findings"]
        == 1
    )

    # ------------------------------------------------------
    # HIDDEN MANAGER FINDING
    # ------------------------------------------------------

    finding_ids = {
        item["id"]
        for item in body[
            "controls"
        ][0]["findings"]
    }

    assert (
        existing_finding.id
        in finding_ids
    )

    assert (
        hidden_finding.id
        not in finding_ids
    )


# ==========================================================
# OVERVIEW SCOPE
# ==========================================================

def test_phase45_overview_is_scope_limited_and_aggregated(
    client,
    users,
    resource_data,
    auth_headers,
):
    employee = users["employee"]

    response = client.get(
        "/api/v1/intelligence/overview",
        headers=_headers(
            auth_headers,
            employee,
        ),
    )

    assert response.status_code == 200

    body = response.json()

    # Employee risk scope is OWN.

    assert (
        body["metrics"]["total_risks"]
        == 1
    )

    assert (
        body["risks"][0]["risk_id"]
        == resource_data[
            "risks"
        ]["employee"].id
    )


# ==========================================================
# AUTHENTICATION
# ==========================================================

def test_phase45_requires_authentication(
    client,
):
    response = client.get(
        "/api/v1/intelligence/overview"
    )

    assert response.status_code == 401


# ==========================================================
# ROUTE REGISTRATION
# ==========================================================

def test_phase45_routes_are_registered(
    client,
):
    response = client.get(
        "/openapi.json"
    )

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert (
        "/api/v1/intelligence/overview"
        in paths
    )

    assert (
        "/api/v1/intelligence/risk/{risk_id}"
        in paths
    )


# ==========================================================
# READ-ONLY
# ==========================================================

def test_phase45_intelligence_is_read_only(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    manager = users["manager"]

    risk = resource_data["risks"]["manager"]

    before = (
        db.query(RiskControl)
        .count()
    )

    response = client.get(
        f"/api/v1/intelligence/risk/{risk.id}",
        headers=_headers(
            auth_headers,
            manager,
        ),
    )

    assert response.status_code == 200

    assert (
        db.query(RiskControl).count()
        == before
    )


# ==========================================================
# CLOSED ACTION
# ==========================================================

def test_phase45_closed_action_is_not_open_or_overdue(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    manager = users["manager"]

    risk = resource_data["risks"]["manager"]

    control = resource_data[
        "controls"
    ]["manager"]

    audit = resource_data[
        "audits"
    ]["manager"]

    existing_action = (
        resource_data[
            "corrective_actions"
        ]["manager"]
    )

    # ------------------------------------------------------
    # RISK -> CONTROL
    # ------------------------------------------------------

    db.add(
        RiskControl(
            risk_id=risk.id,
            control_id=control.id,
        )
    )

    db.commit()

    # ------------------------------------------------------
    # NEW FINDING
    # ------------------------------------------------------

    finding = AuditFinding(
        audit_id=audit.id,
        control_id=control.id,
        title="Closed Action Finding",
        description="Test finding.",
        severity="High",
        recommendation=(
            "No action needed after closure."
        ),
        status="Closed",
    )

    db.add(finding)

    db.commit()

    db.refresh(finding)

    # ------------------------------------------------------
    # NEW CLOSED ACTION
    # ------------------------------------------------------

    closed_action = CorrectiveAction(
        finding_id=finding.id,
        assigned_to=manager.id,
        title="Closed Remediation",
        description="Already completed.",
        priority="High",
        status="Closed",
        due_date=(
            date.today()
            - timedelta(days=10)
        ),
    )

    db.add(closed_action)

    db.commit()

    db.refresh(closed_action)

    # ------------------------------------------------------
    # REQUEST
    # ------------------------------------------------------

    response = client.get(
        f"/api/v1/intelligence/risk/{risk.id}",
        headers=_headers(
            auth_headers,
            manager,
        ),
    )

    assert response.status_code == 200

    body = response.json()

    # ------------------------------------------------------
    # ACTION COUNTS
    # ------------------------------------------------------

    # Existing fixture action + new closed action.

    assert (
        body["metrics"]["action_count"]
        == 2
    )

    # Existing fixture action is Pending.
    # New action is Closed.

    assert (
        body["metrics"]["open_actions"]
        == 1
    )

    # Neither action is overdue:
    # - existing action is due in the future
    # - closed action is excluded from overdue

    assert (
        body["metrics"]["overdue_actions"]
        == 0
    )

    # One of two actions is completed/closed.

    assert (
        body["metrics"][
            "remediation_completion_percent"
        ]
        == 50.0
    )

    # ------------------------------------------------------
    # VERIFY CLOSED ACTION PAYLOAD
    # ------------------------------------------------------

    action_payload = next(
        action_item
        for finding_item in body[
            "controls"
        ][0]["findings"]
        for action_item in finding_item[
            "actions"
        ]
        if action_item["id"]
        == closed_action.id
    )

    assert (
        action_payload["status"]
        == "Closed"
    )

    assert (
        action_payload["overdue"]
        is False
    )