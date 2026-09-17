from datetime import date, timedelta

from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction
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
# OVERVIEW
# ==========================================================

def test_phase46_monitoring_overview_requires_authentication(
    client,
):
    response = client.get(
        "/api/v1/monitoring/overview"
    )

    assert response.status_code == 401


# ==========================================================
# ROUTES
# ==========================================================

def test_phase46_monitoring_routes_are_registered(
    client,
):
    response = client.get(
        "/openapi.json"
    )

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert (
        "/api/v1/monitoring/overview"
        in paths
    )

    assert (
        "/api/v1/monitoring/risk/{risk_id}"
        in paths
    )


# ==========================================================
# CRITICAL RISK
# ==========================================================

def test_phase46_detects_critical_risk(
    client,
    users,
    resource_data,
    auth_headers,
):
    auditor = users["auditor"]

    risk = resource_data[
        "risks"
    ]["auditor"]

    assert risk.risk_score == 20

    response = client.get(
        f"/api/v1/monitoring/risk/{risk.id}",
        headers=_headers(
            auth_headers,
            auditor,
        ),
    )

    assert response.status_code == 200

    body = response.json()

    alert_types = {
        alert["alert_type"]
        for alert in body["alerts"]
    }

    assert (
        "CRITICAL_RISK"
        in alert_types
    )


# ==========================================================
# RISK WITHOUT CONTROL
# ==========================================================

def test_phase46_detects_risk_without_controls(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    manager = users["manager"]

    risk = resource_data[
        "risks"
    ]["manager"]

    # Remove the existing manager risk-control mapping
    # created by the fixture, if present.

    db.query(RiskControl).filter(
        RiskControl.risk_id == risk.id
    ).delete(
        synchronize_session=False
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

    alert_types = {
        alert["alert_type"]
        for alert in body["alerts"]
    }

    assert (
        "RISK_WITHOUT_CONTROLS"
        in alert_types
    )


# ==========================================================
# CONTROL WITHOUT EVIDENCE
# ==========================================================

def test_phase46_detects_control_without_evidence(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    manager = users["manager"]

    risk = resource_data[
        "risks"
    ]["manager"]

    control = resource_data[
        "controls"
    ]["manager"]

    db.add(
        RiskControl(
            risk_id=risk.id,
            control_id=control.id,
        )
    )

    # Remove evidence for this control.

    from app.models.evidence import Evidence

    db.query(Evidence).filter(
        Evidence.control_id == control.id
    ).delete(
        synchronize_session=False
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

    alert_types = {
        alert["alert_type"]
        for alert in body["alerts"]
    }

    assert (
        "CONTROL_WITHOUT_EVIDENCE"
        in alert_types
    )


# ==========================================================
# INEFFECTIVE CONTROL
# ==========================================================

def test_phase46_detects_ineffective_control(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    manager = users["manager"]

    risk = resource_data[
        "risks"
    ]["manager"]

    control = resource_data[
        "controls"
    ]["manager"
    ]

    control.effectiveness = 40

    db.add(
        RiskControl(
            risk_id=risk.id,
            control_id=control.id,
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

    matching_alerts = [
        alert
        for alert in body["alerts"]
        if alert["alert_type"]
        == "INEFFECTIVE_CONTROL"
    ]

    assert len(matching_alerts) >= 1

    assert (
        matching_alerts[0]["resource_id"]
        == control.id
    )


# ==========================================================
# CRITICAL FINDING
# ==========================================================

def test_phase46_detects_critical_finding(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    manager = users["manager"]

    risk = resource_data[
        "risks"
    ]["manager"]

    control = resource_data[
        "controls"
    ]["manager"]

    audit = resource_data[
        "audits"
    ]["manager"]

    db.add(
        RiskControl(
            risk_id=risk.id,
            control_id=control.id,
        )
    )

    finding = AuditFinding(
        audit_id=audit.id,
        control_id=control.id,
        title="Phase 46 Critical Finding",
        description="Monitoring test finding.",
        severity="Critical",
        recommendation="Remediate.",
        status="Open",
    )

    db.add(finding)

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

    critical_findings = [
        alert
        for alert in body["alerts"]
        if alert["alert_type"]
        == "CRITICAL_FINDING"
        and alert["resource_id"]
        == finding.id
    ]

    assert len(
        critical_findings
    ) == 1

    assert (
        critical_findings[0]["severity"]
        == "CRITICAL"
    )


# ==========================================================
# OVERDUE ACTION
# ==========================================================

def test_phase46_detects_overdue_action(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    manager = users["manager"]

    risk = resource_data[
        "risks"
    ]["manager"]

    control = resource_data[
        "controls"
    ]["manager"]

    audit = resource_data[
        "audits"
    ]["manager"]

    db.add(
        RiskControl(
            risk_id=risk.id,
            control_id=control.id,
        )
    )

    finding = AuditFinding(
        audit_id=audit.id,
        control_id=control.id,
        title="Phase 46 Overdue Finding",
        description="Monitoring test finding.",
        severity="High",
        recommendation="Remediate.",
        status="Open",
    )

    db.add(finding)

    db.commit()

    db.refresh(finding)

    action = CorrectiveAction(
        finding_id=finding.id,
        assigned_to=manager.id,
        title="Phase 46 Overdue Action",
        description="Monitoring test action.",
        priority="High",
        status="Pending",
        due_date=(
            date.today()
            - timedelta(days=5)
        ),
    )

    db.add(action)

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

    overdue_alerts = [
        alert
        for alert in body["alerts"]
        if alert["alert_type"]
        == "OVERDUE_ACTION"
        and alert["resource_id"]
        == action.id
    ]

    assert len(
        overdue_alerts
    ) == 1

    assert (
        overdue_alerts[0]["severity"]
        == "HIGH"
    )


# ==========================================================
# COMPLETED ACTION NOT OVERDUE
# ==========================================================

def test_phase46_completed_action_is_not_reported_as_overdue(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    manager = users["manager"]

    risk = resource_data[
        "risks"
    ]["manager"]

    control = resource_data[
        "controls"
    ]["manager"]

    audit = resource_data[
        "audits"
    ]["manager"]

    db.add(
        RiskControl(
            risk_id=risk.id,
            control_id=control.id,
        )
    )

    finding = AuditFinding(
        audit_id=audit.id,
        control_id=control.id,
        title="Phase 46 Completed Finding",
        description="Monitoring test finding.",
        severity="High",
        recommendation="Already remediated.",
        status="Closed",
    )

    db.add(finding)

    db.commit()

    db.refresh(finding)

    action = CorrectiveAction(
        finding_id=finding.id,
        assigned_to=manager.id,
        title="Phase 46 Completed Action",
        description="Already completed.",
        priority="High",
        status="Completed",
        due_date=(
            date.today()
            - timedelta(days=10)
        ),
    )

    db.add(action)

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

    overdue_action_ids = {
        alert["resource_id"]
        for alert in body["alerts"]
        if alert["alert_type"]
        == "OVERDUE_ACTION"
    }

    assert (
        action.id
        not in overdue_action_ids
    )


# ==========================================================
# OUT-OF-SCOPE RISK
# ==========================================================

def test_phase46_hides_out_of_scope_risk(
    client,
    users,
    resource_data,
    auth_headers,
):
    employee = users["employee"]

    admin_risk = resource_data[
        "risks"
    ]["admin"]

    response = client.get(
        f"/api/v1/monitoring/risk/{admin_risk.id}",
        headers=_headers(
            auth_headers,
            employee,
        ),
    )

    assert response.status_code == 404


# ==========================================================
# OVERVIEW IS SCOPE LIMITED
# ==========================================================

def test_phase46_overview_is_scope_limited(
    client,
    users,
    resource_data,
    auth_headers,
):
    employee = users["employee"]

    response = client.get(
        "/api/v1/monitoring/overview",
        headers=_headers(
            auth_headers,
            employee,
        ),
    )

    assert response.status_code == 200

    body = response.json()

    # Employee has OWN risk visibility.

    assert (
        body["metrics"]["critical_risks"]
        == 0
    )

    risk_ids = {
        alert["risk_id"]
        for alert in body["alerts"]
        if alert["risk_id"] is not None
    }

    employee_risk = resource_data[
        "risks"
    ]["employee"]

    for risk_id in risk_ids:
        assert (
            risk_id
            == employee_risk.id
        )


# ==========================================================
# READ-ONLY
# ==========================================================

def test_phase46_monitoring_is_read_only(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    manager = users["manager"]

    risk = resource_data[
        "risks"
    ]["manager"]

    before_risks = db.query(
        RiskControl
    ).count()

    response = client.get(
        f"/api/v1/monitoring/risk/{risk.id}",
        headers=_headers(
            auth_headers,
            manager,
        ),
    )

    assert response.status_code == 200

    after_risks = db.query(
        RiskControl
    ).count()

    assert (
        before_risks
        == after_risks
    )