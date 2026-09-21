from datetime import date, timedelta
from io import BytesIO


def _headers(auth_headers, user):
    return auth_headers(user)


def _json(response):
    return response.json()


def _build_lifecycle(client, manager, headers, monkeypatch, tmp_path):
    risk_response = client.post(
        "/api/v1/risks/",
        headers=headers,
        json={
            "title": "Phase 53.2 State Propagation Risk",
            "description": "Risk used to verify downstream state propagation.",
            "likelihood": 5,
            "impact": 5,
            "owner_id": manager.id,
        },
    )
    assert risk_response.status_code == 200
    risk_id = _json(risk_response)["id"]

    control_response = client.post(
        "/api/v1/controls/",
        headers=headers,
        json={
            "title": "Phase 53.2 Propagation Control",
            "description": "Control used to verify downstream state propagation.",
            "control_type": "Preventive",
            "status": "Active",
            "effectiveness": 80,
            "owner_id": manager.id,
        },
    )
    assert control_response.status_code == 200
    control_id = _json(control_response)["id"]

    mapping_response = client.post(
        "/api/v1/risk-controls/",
        headers=headers,
        json={
            "risk_id": risk_id,
            "control_id": control_id,
        },
    )
    assert mapping_response.status_code == 200

    from app.api.v1.routes import evidence as evidence_route

    monkeypatch.setattr(evidence_route, "UPLOAD_DIR", tmp_path)

    evidence_response = client.post(
        "/api/v1/evidence/",
        headers=headers,
        data={
            "control_id": str(control_id),
            "title": "Phase 53.2 Evidence",
            "description": "Evidence used to verify downstream state propagation.",
        },
        files={
            "file": (
                "phase532-evidence.pdf",
                BytesIO(b"%PDF-1.4 phase 53.2 evidence"),
                "application/pdf",
            )
        },
    )
    assert evidence_response.status_code == 200

    framework_response = client.post(
        "/api/v1/frameworks/",
        headers=headers,
        json={
            "name": "Phase 53.2 Propagation Framework",
            "version": "1.0",
            "description": "Framework used to verify downstream state propagation.",
        },
    )
    assert framework_response.status_code == 200
    framework_id = _json(framework_response)["id"]

    audit_response = client.post(
        "/api/v1/audits/",
        headers=headers,
        json={
            "name": "Phase 53.2 Propagation Audit",
            "framework_id": framework_id,
            "auditor_id": manager.id,
            "scope": "State propagation verification",
            "status": "In Progress",
            "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=30)).isoformat(),
        },
    )
    assert audit_response.status_code == 200
    audit_id = _json(audit_response)["id"]

    finding_response = client.post(
        "/api/v1/audit-findings/",
        headers=headers,
        json={
            "audit_id": audit_id,
            "control_id": control_id,
            "title": "Phase 53.2 Critical Finding",
            "description": "Critical finding used to verify state propagation.",
            "severity": "Critical",
            "recommendation": "Resolve the finding and verify the remediation.",
            "status": "Open",
        },
    )
    assert finding_response.status_code == 200
    finding_id = _json(finding_response)["id"]

    overdue_date = date.today() - timedelta(days=1)

    action_response = client.post(
        "/api/v1/corrective-actions/",
        headers=headers,
        json={
            "finding_id": finding_id,
            "assigned_to": manager.id,
            "title": "Phase 53.2 Critical Remediation",
            "description": "Remediation action used to verify state propagation.",
            "priority": "Critical",
            "status": "Open",
            "due_date": overdue_date.isoformat(),
            "comments": "Phase 53.2 state transition test.",
        },
    )
    assert action_response.status_code == 200
    action_id = _json(action_response)["id"]

    return risk_id, control_id, finding_id, action_id


def test_phase53_state_transitions_propagate_to_intelligence_and_monitoring(
    client,
    users,
    auth_headers,
    monkeypatch,
    tmp_path,
):
    """Verify lifecycle state changes immediately propagate downstream."""

    manager = users["manager"]
    headers = _headers(auth_headers, manager)

    risk_id, control_id, finding_id, action_id = _build_lifecycle(
        client,
        manager,
        headers,
        monkeypatch,
        tmp_path,
    )

    # ---------------------------------------------------------
    # INITIAL STATE
    # ---------------------------------------------------------

    intelligence_response = client.get(
        f"/api/v1/intelligence/risk/{risk_id}",
        headers=headers,
    )
    assert intelligence_response.status_code == 200
    metrics = _json(intelligence_response)["metrics"]

    assert metrics["control_count"] == 1
    assert metrics["controls_with_evidence"] == 1
    assert metrics["evidence_coverage_percent"] == 100.0
    assert metrics["finding_count"] == 1
    assert metrics["open_findings"] == 1
    assert metrics["critical_findings"] == 1
    assert metrics["action_count"] == 1
    assert metrics["open_actions"] == 1
    assert metrics["overdue_actions"] == 1
    assert metrics["remediation_completion_percent"] == 0.0

    monitoring_response = client.get(
        f"/api/v1/monitoring/risk/{risk_id}",
        headers=headers,
    )
    assert monitoring_response.status_code == 200
    initial_alert_types = {
        item["alert_type"]
        for item in _json(monitoring_response)["alerts"]
    }

    assert "CRITICAL_RISK" in initial_alert_types
    assert "CRITICAL_FINDING" in initial_alert_types
    assert "OPEN_FINDING" in initial_alert_types
    assert "CRITICAL_ACTION" in initial_alert_types
    assert "OVERDUE_ACTION" in initial_alert_types

    # ---------------------------------------------------------
    # COMPLETE CORRECTIVE ACTION
    # ---------------------------------------------------------

    completed_action_response = client.patch(
        f"/api/v1/corrective-actions/{action_id}",
        headers=headers,
        json={
            "status": "Completed",
            "completed_at": date.today().isoformat(),
        },
    )
    assert completed_action_response.status_code == 200
    completed_action = _json(completed_action_response)
    assert completed_action["status"] == "Completed"

    intelligence_after_action = client.get(
        f"/api/v1/intelligence/risk/{risk_id}",
        headers=headers,
    )
    assert intelligence_after_action.status_code == 200
    action_metrics = _json(intelligence_after_action)["metrics"]

    assert action_metrics["action_count"] == 1
    assert action_metrics["open_actions"] == 0
    assert action_metrics["overdue_actions"] == 0
    assert action_metrics["remediation_completion_percent"] == 100.0

    monitoring_after_action = client.get(
        f"/api/v1/monitoring/risk/{risk_id}",
        headers=headers,
    )
    assert monitoring_after_action.status_code == 200
    alert_types_after_action = {
        item["alert_type"]
        for item in _json(monitoring_after_action)["alerts"]
    }

    assert "CRITICAL_RISK" in alert_types_after_action
    assert "CRITICAL_FINDING" in alert_types_after_action
    assert "OPEN_FINDING" in alert_types_after_action
    assert "CRITICAL_ACTION" not in alert_types_after_action
    assert "OVERDUE_ACTION" not in alert_types_after_action

    # ---------------------------------------------------------
    # CLOSE FINDING
    # ---------------------------------------------------------

    closed_finding_response = client.patch(
        f"/api/v1/audit-findings/{finding_id}",
        headers=headers,
        json={
            "status": "Closed",
        },
    )
    assert closed_finding_response.status_code == 200
    closed_finding = _json(closed_finding_response)
    assert closed_finding["status"] == "Closed"

    intelligence_after_finding = client.get(
        f"/api/v1/intelligence/risk/{risk_id}",
        headers=headers,
    )
    assert intelligence_after_finding.status_code == 200
    finding_metrics = _json(intelligence_after_finding)["metrics"]

    assert finding_metrics["finding_count"] == 1
    assert finding_metrics["open_findings"] == 0
    assert finding_metrics["critical_findings"] == 1
    assert finding_metrics["action_count"] == 1
    assert finding_metrics["open_actions"] == 0

    monitoring_after_finding = client.get(
        f"/api/v1/monitoring/risk/{risk_id}",
        headers=headers,
    )
    assert monitoring_after_finding.status_code == 200
    alert_types_after_finding = {
        item["alert_type"]
        for item in _json(monitoring_after_finding)["alerts"]
    }

    assert "CRITICAL_RISK" in alert_types_after_finding
    assert "CRITICAL_FINDING" in alert_types_after_finding
    assert "OPEN_FINDING" not in alert_types_after_finding
    assert "CRITICAL_ACTION" not in alert_types_after_finding
    assert "OVERDUE_ACTION" not in alert_types_after_finding
