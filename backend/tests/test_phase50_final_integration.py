"""
Phase 50 — Final Integration Audit

This module tests the interaction between the major CyberGRC-AI
security and GRC subsystems.

The focus is not individual endpoint authorization, which is already
covered extensively elsewhere. Instead, these tests verify that
authorization boundaries remain intact when data flows across:

    Risk
      ↓
    Control
      ↓
    Evidence
      ↓
    Audit Finding
      ↓
    Corrective Action

and through:

    Dashboard
    Reports
    GRC Intelligence
    Continuous Monitoring
    AI authorization

The production implementation is intentionally not modified by
this test module.

Expected security semantics:

    401 = unauthenticated
    403 = authenticated but lacks permission
    404 = requested resource is outside visibility scope
"""


from datetime import date, timedelta

import pytest

from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction
from app.models.risk_control import RiskControl


# ==========================================================
# HELPERS
# ==========================================================


def _headers(auth_headers, user):
    return auth_headers(user)


# ==========================================================
# 1. RISK -> CONTROL INTEGRATION
# ==========================================================


def test_phase50_risk_control_relationship_respects_control_scope(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    """
    A visible Risk must not become a gateway to Controls that
    are outside the requesting user's Control visibility scope.

    Scenario:

        Manager
          ↓
        Manager Risk
          ↓
        Admin Control

    The Manager can see the Risk, but the Admin-owned Control is
    outside the Manager's SUBORDINATES control scope.

    The relationship endpoint must therefore not expose the
    Admin Control.
    """

    manager = users["manager"]

    risk = resource_data["risks"]["manager"]

    visible_control = resource_data["controls"]["manager"]

    out_of_scope_control = resource_data["controls"]["admin"]

    db.add(
        RiskControl(
            risk_id=risk.id,
            control_id=visible_control.id,
        )
    )

    db.add(
        RiskControl(
            risk_id=risk.id,
            control_id=out_of_scope_control.id,
        )
    )

    db.commit()

    response = client.get(
        f"/api/v1/risk-controls/risk/{risk.id}",
        headers=_headers(
            auth_headers,
            manager,
        ),
    )

    assert response.status_code == 200

    body = response.json()

    returned_control_ids = {
        control["id"]
        for control in body
    }

    assert visible_control.id in returned_control_ids

    assert (
        out_of_scope_control.id
        not in returned_control_ids
    )


# ==========================================================
# 2. CONTROL -> RISK INTEGRATION
# ==========================================================


def test_phase50_control_risk_relationship_respects_risk_scope(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    """
    A visible Control must not become a gateway to Risks outside
    the requesting user's Risk visibility scope.

    Scenario:

        Manager Control
          ├── Manager Risk
          └── Admin Risk

    The Manager cannot see the Admin Risk.
    """

    manager = users["manager"]

    control = resource_data["controls"]["manager"]

    visible_risk = resource_data["risks"]["manager"]

    out_of_scope_risk = resource_data["risks"]["admin"]

    db.add(
        RiskControl(
            risk_id=visible_risk.id,
            control_id=control.id,
        )
    )

    db.add(
        RiskControl(
            risk_id=out_of_scope_risk.id,
            control_id=control.id,
        )
    )

    db.commit()

    response = client.get(
        f"/api/v1/risk-controls/control/{control.id}",
        headers=_headers(
            auth_headers,
            manager,
        ),
    )

    assert response.status_code == 200

    body = response.json()

    returned_risk_ids = {
        risk["id"]
        for risk in body
    }

    assert visible_risk.id in returned_risk_ids

    assert (
        out_of_scope_risk.id
        not in returned_risk_ids
    )


# ==========================================================
# 3. GRC INTELLIGENCE CROSS-SCOPE DEFENSE
# ==========================================================


def test_phase50_intelligence_does_not_cross_control_visibility_boundary(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    """
    GRC Intelligence must not expose an out-of-scope Control merely
    because that Control is linked to an in-scope Risk.

    Scenario:

        Manager
          ↓
        Manager Risk
          ├── Manager Control
          └── Admin Control

    Only the Manager Control should appear in intelligence.
    """

    manager = users["manager"]

    risk = resource_data["risks"]["manager"]

    visible_control = resource_data["controls"]["manager"]

    out_of_scope_control = resource_data["controls"]["admin"]

    db.add(
        RiskControl(
            risk_id=risk.id,
            control_id=visible_control.id,
        )
    )

    db.add(
        RiskControl(
            risk_id=risk.id,
            control_id=out_of_scope_control.id,
        )
    )

    db.commit()

    response = client.get(
        f"/api/v1/intelligence/risk/{risk.id}",
        headers=_headers(
            auth_headers,
            manager,
        ),
    )

    assert response.status_code == 200

    body = response.json()

    returned_control_ids = {
        control["id"]
        for control in body["controls"]
    }

    assert visible_control.id in returned_control_ids

    assert (
        out_of_scope_control.id
        not in returned_control_ids
    )


# ==========================================================
# 4. MONITORING CROSS-SCOPE DEFENSE
# ==========================================================


def test_phase50_monitoring_does_not_generate_alerts_from_out_of_scope_controls(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    """
    Continuous Monitoring must not inspect an out-of-scope Control
    simply because that Control is mapped to an in-scope Risk.

    An Admin-owned ineffective Control is deliberately attached
    to a Manager-owned Risk.

    The Manager must not receive a monitoring alert for that
    Admin-owned Control.
    """

    manager = users["manager"]

    risk = resource_data["risks"]["manager"]

    out_of_scope_control = resource_data["controls"]["admin"]

    out_of_scope_control.effectiveness = 20

    db.add(
        RiskControl(
            risk_id=risk.id,
            control_id=out_of_scope_control.id,
        )
    )

    db.commit()

    response = client.get(
        f"/api/v1/monitoring/risk/{risk.id}",
        headers=_headers(
            auth_headers,
            manager,
        ),
    )

    assert response.status_code == 200

    body = response.json()

    leaked_alerts = [
        alert
        for alert in body["alerts"]
        if (
            alert.get("resource_id")
            == out_of_scope_control.id
            and alert.get("resource_type")
            == "control"
        )
    ]

    assert leaked_alerts == []


# ==========================================================
# 5. DASHBOARD SCOPE INTEGRATION
# ==========================================================


def test_phase50_dashboard_metrics_match_manager_resource_scope(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    Dashboard metrics must use the same visibility model as the
    underlying GRC resources.

    The fixture contains five resources per major resource type:

        Admin
        Manager
        Analyst
        Auditor
        Employee

    A GRC Manager has SUBORDINATES visibility, so Admin-owned
    resources must not contribute to scoped metrics.
    """

    manager = users["manager"]

    response = client.get(
        "/api/v1/dashboard/",
        headers=_headers(
            auth_headers,
            manager,
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["totalRisks"] == 4

    assert body["controls"] == 4

    assert body["totalEvidence"] == 4

    assert body["audits"] == 4

    assert body["totalFindings"] == 4

    assert body["totalActions"] == 4


# ==========================================================
# 6. RISK REPORT SCOPE INTEGRATION
# ==========================================================


def test_phase50_risk_report_respects_resource_scope(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    Risk reports must contain only Risks visible to the requesting
    user.
    """

    manager = users["manager"]

    response = client.get(
        "/api/v1/reports/risks",
        headers=_headers(
            auth_headers,
            manager,
        ),
    )

    assert response.status_code == 200

    body = response.json()

    returned_risk_ids = {
        risk["id"]
        for risk in body["risks"]
    }

    expected_ids = {
        resource_data["risks"][role].id
        for role in (
            "manager",
            "analyst",
            "auditor",
            "employee",
        )
    }

    assert returned_risk_ids == expected_ids

    assert (
        resource_data["risks"]["admin"].id
        not in returned_risk_ids
    )

    assert body["summary"]["total_risks"] == 4


# ==========================================================
# 7. AUDIT REPORT + FINDING INTEGRATION
# ==========================================================


def test_phase50_audit_report_does_not_cross_audit_scope(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    Audit reports must restrict both the Audit list and its
    aggregated Findings to audits within the user's visibility
    scope.
    """

    manager = users["manager"]

    response = client.get(
        "/api/v1/reports/audits",
        headers=_headers(
            auth_headers,
            manager,
        ),
    )

    assert response.status_code == 200

    body = response.json()

    returned_audit_ids = {
        audit["id"]
        for audit in body["audits"]
    }

    expected_ids = {
        resource_data["audits"][role].id
        for role in (
            "manager",
            "analyst",
            "auditor",
            "employee",
        )
    }

    assert returned_audit_ids == expected_ids

    assert (
        resource_data["audits"]["admin"].id
        not in returned_audit_ids
    )

    assert body["summary"]["total_audits"] == 4

    assert body["summary"]["total_findings"] == 4


# ==========================================================
# 8. COMPLIANCE REPORT INTEGRATION
# ==========================================================


def test_phase50_compliance_report_respects_control_and_audit_scope(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    Compliance reporting must not expose Admin-owned controls,
    evidence, or findings through a report generated for a
    GRC Manager.
    """

    manager = users["manager"]

    response = client.get(
        "/api/v1/reports/compliance",
        headers=_headers(
            auth_headers,
            manager,
        ),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["summary"]["total_controls"] == 4

    assert body["summary"]["total_evidence"] == 4

    assert body["summary"]["total_findings"] == 4

    assert (
        body["summary"]["total_controls"]
        == len(
            {
                resource_data["controls"][role].id
                for role in (
                    "manager",
                    "analyst",
                    "auditor",
                    "employee",
                )
            }
        )
    )


# ==========================================================
# 9. AI GENERIC ACCESS RESPECTS RISK VISIBILITY
# ==========================================================


def test_phase50_generic_ai_cannot_cross_risk_visibility_boundary(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    Generic AI may be available to an authorized role, but the AI
    endpoint must still reject an out-of-scope Risk before invoking
    the AI service.

    The Analyst has generic AI permission only through the existing
    authorization contract where applicable; the important property
    here is that an Admin-owned Risk cannot be passed through the
    Analyst's visibility boundary.
    """

    analyst = users["analyst"]

    admin_risk = resource_data["risks"]["admin"]

    response = client.post(
        f"/api/v1/ai/risk/{admin_risk.id}/analyze",
        headers=_headers(
            auth_headers,
            analyst,
        ),
    )

    assert response.status_code == 403


# ==========================================================
# 10. AI EXECUTIVE SUMMARY ROLE BOUNDARY
# ==========================================================


@pytest.mark.parametrize(
    "role_key",
    [
        "admin",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_phase50_non_manager_roles_cannot_use_executive_ai_summary(
    client,
    users,
    auth_headers,
    role_key,
):
    """
    The dedicated AI Executive Summary permission remains restricted
    to the GRC Manager.

    These requests must fail before any AI provider invocation.
    """

    user = users[role_key]

    response = client.get(
        "/api/v1/ai/dashboard/executive-summary",
        headers=_headers(
            auth_headers,
            user,
        ),
    )

    assert response.status_code == 403


# ==========================================================
# 11. FULL GRC CHAIN — VISIBLE DATA
# ==========================================================


def test_phase50_full_grc_chain_remains_visible_within_scope(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    """
    Verify that a complete in-scope relationship remains available
    when the Risk, Control, Audit, Finding, and Corrective Action
    all belong to the Manager's visible organizational scope.

        Risk
          ↓
        Control
          ↓
        Evidence
          ↓
        Audit Finding
          ↓
        Corrective Action
    """

    manager = users["manager"]

    risk = resource_data["risks"]["manager"]

    control = resource_data["controls"]["manager"]

    audit = resource_data["audits"]["manager"]

    finding = resource_data["findings"]["manager"]

    action = resource_data["corrective_actions"]["manager"]

    db.add(
        RiskControl(
            risk_id=risk.id,
            control_id=control.id,
        )
    )

    db.commit()

    # ------------------------------------------------------
    # RISK -> CONTROL
    # ------------------------------------------------------

    risk_control_response = client.get(
        f"/api/v1/risk-controls/risk/{risk.id}",
        headers=_headers(
            auth_headers,
            manager,
        ),
    )

    assert risk_control_response.status_code == 200

    risk_control_ids = {
        item["id"]
        for item in risk_control_response.json()
    }

    assert control.id in risk_control_ids

    # ------------------------------------------------------
    # INTELLIGENCE
    # ------------------------------------------------------

    intelligence_response = client.get(
        f"/api/v1/intelligence/risk/{risk.id}",
        headers=_headers(
            auth_headers,
            manager,
        ),
    )

    assert intelligence_response.status_code == 200

    intelligence = intelligence_response.json()

    assert intelligence["risk_id"] == risk.id

    intelligence_control_ids = {
        item["id"]
        for item in intelligence["controls"]
    }

    assert control.id in intelligence_control_ids

    # ------------------------------------------------------
    # MONITORING
    # ------------------------------------------------------

    monitoring_response = client.get(
        f"/api/v1/monitoring/risk/{risk.id}",
        headers=_headers(
            auth_headers,
            manager,
        ),
    )

    assert monitoring_response.status_code == 200

    monitoring = monitoring_response.json()

    assert monitoring["risk_id"] == risk.id

    # ------------------------------------------------------
    # EXISTING FINDING/ACTION CHAIN
    # ------------------------------------------------------

    assert finding.audit_id == audit.id

    assert action.finding_id == finding.id

    assert action.assigned_to == manager.id


# ==========================================================
# 12. OUT-OF-SCOPE INTELLIGENCE OBJECT
# ==========================================================


def test_phase50_out_of_scope_risk_is_hidden_from_intelligence(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    A permitted intelligence user must receive the same 404
    object-hiding behavior when requesting a Risk outside their
    visibility scope.
    """

    analyst = users["analyst"]

    admin_risk = resource_data["risks"]["admin"]

    response = client.get(
        f"/api/v1/intelligence/risk/{admin_risk.id}",
        headers=_headers(
            auth_headers,
            analyst,
        ),
    )

    assert response.status_code == 404


# ==========================================================
# 13. OUT-OF-SCOPE MONITORING OBJECT
# ==========================================================


def test_phase50_out_of_scope_risk_is_hidden_from_monitoring(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    Continuous Monitoring must preserve the same object-level
    visibility boundary as the underlying Risk API.
    """

    analyst = users["analyst"]

    admin_risk = resource_data["risks"]["admin"]

    response = client.get(
        f"/api/v1/monitoring/risk/{admin_risk.id}",
        headers=_headers(
            auth_headers,
            analyst,
        ),
    )

    assert response.status_code == 404


# ==========================================================
# 14. CORRECTIVE ACTION CHAIN INTEGRATION
# ==========================================================


def test_phase50_corrective_action_visibility_matches_finding_scope(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    A corrective action must not become a side channel for an
    out-of-scope Audit Finding.

    The Analyst can see the Analyst finding/action, but not the
    Admin finding/action.
    """

    analyst = users["analyst"]

    visible_action = (
        resource_data["corrective_actions"]["analyst"]
    )

    out_of_scope_action = (
        resource_data["corrective_actions"]["admin"]
    )

    response = client.get(
        "/api/v1/corrective-actions/",
        headers=_headers(
            auth_headers,
            analyst,
        ),
    )

    assert response.status_code == 200

    body = response.json()

    returned_ids = {
        item["id"]
        for item in body
    }

    assert visible_action.id in returned_ids

    assert (
        out_of_scope_action.id
        not in returned_ids
    )


# ==========================================================
# 15. UNAUTHENTICATED INTEGRATION BOUNDARY
# ==========================================================


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/v1/dashboard/",
        "/api/v1/reports/risks",
        "/api/v1/reports/audits",
        "/api/v1/reports/compliance",
        "/api/v1/intelligence/overview",
        "/api/v1/monitoring/overview",
    ],
)
def test_phase50_integrated_read_surfaces_require_authentication(
    client,
    endpoint,
):
    """
    All major integrated read surfaces must reject unauthenticated
    requests.
    """

    response = client.get(endpoint)

    assert response.status_code == 401