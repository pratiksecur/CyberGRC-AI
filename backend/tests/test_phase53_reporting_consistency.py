from datetime import date, timedelta
from io import BytesIO


def _json(response):
    return response.json()


def _headers(auth_headers, user):
    return auth_headers(user)


def _create_chain(client, manager, headers, monkeypatch, tmp_path):
    risk_response = client.post(
        "/api/v1/risks/",
        headers=headers,
        json={
            "title": "Phase 53.3 Reporting Consistency Risk",
            "description": "Risk used to verify cross-surface reporting consistency.",
            "likelihood": 5,
            "impact": 5,
            "owner_id": manager.id,
        },
    )
    assert risk_response.status_code == 200
    risk = _json(risk_response)

    control_response = client.post(
        "/api/v1/controls/",
        headers=headers,
        json={
            "title": "Phase 53.3 Reporting Consistency Control",
            "description": "Control used to verify cross-surface reporting consistency.",
            "control_type": "Preventive",
            "status": "Active",
            "effectiveness": 80,
            "owner_id": manager.id,
        },
    )
    assert control_response.status_code == 200
    control = _json(control_response)

    mapping_response = client.post(
        "/api/v1/risk-controls/",
        headers=headers,
        json={
            "risk_id": risk["id"],
            "control_id": control["id"],
        },
    )
    assert mapping_response.status_code == 200

    framework_response = client.post(
        "/api/v1/frameworks/",
        headers=headers,
        json={
            "name": "Phase 53.3 Reporting Framework",
            "version": "1.0",
            "description": "Framework used for reporting consistency verification.",
        },
    )
    assert framework_response.status_code == 200
    framework = _json(framework_response)

    framework_control_response = client.post(
        "/api/v1/framework-controls/",
        headers=headers,
        json={
            "framework_id": framework["id"],
            "control_code": "P53.3",
            "title": "Reporting Consistency Requirement",
            "description": "Requirement used for reporting consistency verification.",
        },
    )
    assert framework_control_response.status_code == 200
    framework_control = _json(framework_control_response)

    control_framework_response = client.post(
        "/api/v1/control-framework-controls/",
        headers=headers,
        json={
            "control_id": control["id"],
            "framework_control_id": framework_control["id"],
        },
    )
    assert control_framework_response.status_code == 200

    from app.api.v1.routes import evidence as evidence_route

    monkeypatch.setattr(evidence_route, "UPLOAD_DIR", tmp_path)

    evidence_response = client.post(
        "/api/v1/evidence/",
        headers=headers,
        data={
            "control_id": str(control["id"]),
            "title": "Phase 53.3 Reporting Evidence",
            "description": "Evidence used to verify reporting consistency.",
        },
        files={
            "file": (
                "phase533-evidence.pdf",
                BytesIO(b"%PDF-1.4 phase 53.3 reporting evidence"),
                "application/pdf",
            )
        },
    )
    assert evidence_response.status_code == 200
    evidence = _json(evidence_response)

    audit_response = client.post(
        "/api/v1/audits/",
        headers=headers,
        json={
            "name": "Phase 53.3 Reporting Audit",
            "framework_id": framework["id"],
            "auditor_id": manager.id,
            "scope": "Reporting consistency verification",
            "status": "In Progress",
            "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=30)).isoformat(),
        },
    )
    assert audit_response.status_code == 200
    audit = _json(audit_response)

    finding_response = client.post(
        "/api/v1/audit-findings/",
        headers=headers,
        json={
            "audit_id": audit["id"],
            "control_id": control["id"],
            "title": "Phase 53.3 Critical Reporting Finding",
            "description": "Critical finding used to verify consistent reporting.",
            "severity": "Critical",
            "recommendation": "Correct the reporting consistency issue and retain evidence.",
            "status": "Open",
        },
    )
    assert finding_response.status_code == 200
    finding = _json(finding_response)

    action_response = client.post(
        "/api/v1/corrective-actions/",
        headers=headers,
        json={
            "finding_id": finding["id"],
            "assigned_to": manager.id,
            "title": "Phase 53.3 Critical Remediation",
            "description": "Remediate the critical finding for consistency verification.",
            "priority": "Critical",
            "status": "Open",
            "due_date": (date.today() - timedelta(days=1)).isoformat(),
            "comments": "Phase 53.3 reporting consistency test.",
        },
    )
    assert action_response.status_code == 200
    action = _json(action_response)

    return {
        "risk": risk,
        "control": control,
        "framework": framework,
        "framework_control": framework_control,
        "evidence": evidence,
        "audit": audit,
        "finding": finding,
        "action": action,
    }


def test_phase53_reporting_surfaces_are_consistent(
    client,
    users,
    auth_headers,
    monkeypatch,
    tmp_path,
):
    """Verify intelligence, monitoring, reports, and dashboard tell the same story."""

    manager = users["manager"]
    headers = _headers(auth_headers, manager)

    chain = _create_chain(
        client,
        manager,
        headers,
        monkeypatch,
        tmp_path,
    )

    risk_id = chain["risk"]["id"]
    control_id = chain["control"]["id"]
    framework_id = chain["framework"]["id"]
    framework_control_id = chain["framework_control"]["id"]
    evidence_id = chain["evidence"]["id"]
    audit_id = chain["audit"]["id"]
    finding_id = chain["finding"]["id"]
    action_id = chain["action"]["id"]

    # ---------------------------------------------------------
    # GRC INTELLIGENCE — AUTHORITATIVE RELATIONSHIP SNAPSHOT
    # ---------------------------------------------------------

    intelligence_response = client.get(
        f"/api/v1/intelligence/risk/{risk_id}",
        headers=headers,
    )
    assert intelligence_response.status_code == 200
    intelligence = _json(intelligence_response)
    metrics = intelligence["metrics"]

    assert intelligence["risk_score"] == 25
    assert metrics["control_count"] == 1
    assert metrics["controls_with_evidence"] == 1
    assert metrics["evidence_coverage_percent"] == 100.0
    assert metrics["average_control_effectiveness"] == 80.0
    assert metrics["framework_count"] == 1
    assert metrics["finding_count"] == 1
    assert metrics["open_findings"] == 1
    assert metrics["critical_findings"] == 1
    assert metrics["action_count"] == 1
    assert metrics["open_actions"] == 1
    assert metrics["overdue_actions"] == 1
    assert metrics["remediation_completion_percent"] == 0.0
    assert metrics["estimated_residual_risk"] == 5.0

    graph_control = intelligence["controls"][0]
    assert graph_control["id"] == control_id
    assert graph_control["evidence"][0]["id"] == evidence_id
    assert graph_control["frameworks"][0]["id"] == framework_id
    assert graph_control["frameworks"][0]["control_code"] == "P53.3"
    assert graph_control["findings"][0]["id"] == finding_id
    assert graph_control["findings"][0]["actions"][0]["id"] == action_id

    # ---------------------------------------------------------
    # MONITORING — SAME ACTIVE CONDITIONS
    # ---------------------------------------------------------

    monitoring_response = client.get(
        f"/api/v1/monitoring/risk/{risk_id}",
        headers=headers,
    )
    assert monitoring_response.status_code == 200
    monitoring = _json(monitoring_response)

    assert monitoring["risk_id"] == risk_id
    assert monitoring["risk_score"] == 25

    alert_types = {
        alert["alert_type"]
        for alert in monitoring["alerts"]
    }

    assert "CRITICAL_RISK" in alert_types
    assert "CRITICAL_FINDING" in alert_types
    assert "OPEN_FINDING" in alert_types
    assert "CRITICAL_ACTION" in alert_types
    assert "OVERDUE_ACTION" in alert_types
    assert "RISK_WITHOUT_CONTROLS" not in alert_types
    assert "CONTROL_WITHOUT_EVIDENCE" not in alert_types

    # ---------------------------------------------------------
    # RISK REPORT — SAME RISK STATE
    # ---------------------------------------------------------

    risk_report_response = client.get(
        "/api/v1/reports/risks",
        headers=headers,
    )
    assert risk_report_response.status_code == 200
    risk_report = _json(risk_report_response)

    assert risk_report["summary"]["total_risks"] == 1
    assert risk_report["summary"]["critical_risks"] == 1
    assert risk_report["summary"]["average_risk_score"] == 25.0
    assert risk_report["risks"][0]["id"] == risk_id
    assert risk_report["risks"][0]["risk_score"] == 25

    # ---------------------------------------------------------
    # AUDIT REPORT — SAME FINDING STATE
    # ---------------------------------------------------------

    audit_report_response = client.get(
        "/api/v1/reports/audits",
        headers=headers,
    )
    assert audit_report_response.status_code == 200
    audit_report = _json(audit_report_response)

    assert audit_report["summary"]["total_audits"] == 1
    assert audit_report["summary"]["in_progress_audits"] == 1
    assert audit_report["summary"]["total_findings"] == 1
    assert audit_report["summary"]["critical_findings"] == 1
    assert audit_report["summary"]["open_findings"] == 1

    audit_item = audit_report["audits"][0]
    assert audit_item["id"] == audit_id
    assert audit_item["finding_count"] == 1
    assert audit_item["critical_finding_count"] == 1
    assert audit_item["open_finding_count"] == 1

    # ---------------------------------------------------------
    # COMPLIANCE REPORT — SAME CONTROL/EVIDENCE/FINDING STATE
    # ---------------------------------------------------------

    compliance_response = client.get(
        "/api/v1/reports/compliance",
        headers=headers,
    )
    assert compliance_response.status_code == 200
    compliance = _json(compliance_response)

    assert compliance["summary"]["total_frameworks"] == 1
    assert compliance["summary"]["total_controls"] == 1
    assert compliance["summary"]["active_controls"] == 1
    assert compliance["summary"]["average_control_effectiveness"] == 80.0
    assert compliance["summary"]["total_evidence"] == 1
    assert compliance["summary"]["total_findings"] == 1
    assert compliance["summary"]["open_findings"] == 1
    assert compliance["summary"]["critical_findings"] == 1

    framework_item = compliance["frameworks"][0]
    assert framework_item["id"] == framework_id
    assert framework_item["control_count"] == 1
    assert framework_item["active_control_count"] == 1
    assert framework_item["average_effectiveness"] == 80.0
    assert framework_item["evidence_count"] == 1
    assert framework_item["finding_count"] == 1
    assert framework_item["critical_finding_count"] == 1
    assert framework_item["open_finding_count"] == 1

    # ---------------------------------------------------------
    # DASHBOARD — SAME AGGREGATED STATE
    # ---------------------------------------------------------

    dashboard_response = client.get(
        "/api/v1/dashboard/",
        headers=headers,
    )
    assert dashboard_response.status_code == 200
    dashboard = _json(dashboard_response)

    assert dashboard["totalRisks"] == 1
    assert dashboard["criticalRisks"] == 1
    assert dashboard["controls"] == 1
    assert dashboard["activeControls"] == 1
    assert dashboard["totalEvidence"] == 1
    assert dashboard["audits"] == 1
    assert dashboard["compliance"] == 80
    assert dashboard["securityHealth"] == 40
    assert dashboard["totalFindings"] == 1
    assert dashboard["openFindings"] == 1
    assert dashboard["criticalFindings"] == 1
    assert dashboard["totalActions"] == 1
    assert dashboard["pendingActions"] == 1
    assert dashboard["overdueActions"] == 1

    remediation = dashboard["criticalRemediation"]
    assert remediation is not None
    assert remediation["findingId"] == finding_id
    assert remediation["actionId"] == action_id
    assert remediation["findingSeverity"] == "Critical"
    assert remediation["priority"] == "Critical"
    assert remediation["status"] == "Open"
