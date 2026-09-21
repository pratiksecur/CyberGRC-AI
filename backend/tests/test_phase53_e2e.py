"""
Phase 53.1 — End-to-End GRC Lifecycle

Exercises one complete manager-owned GRC workflow through the real
FastAPI endpoints and verifies that downstream intelligence, monitoring,
reports, and AI consumers see the resulting state.

Workflow:

    Risk
      ↓
    Control
      ↓
    Risk-Control Mapping
      ↓
    Framework
      ↓
    Framework Requirement
      ↓
    Control-Framework Mapping
      ↓
    Evidence
      ↓
    Audit
      ↓
    Audit Finding
      ↓
    Corrective Action
      ↓
    GRC Intelligence / Monitoring / Reports / AI

The production implementation is intentionally not modified by this test.
"""

from datetime import date, timedelta
from io import BytesIO
import json


class FakeProvider:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0
        self.prompts = []
        self.model = "phase53-test-model"

    def generate(self, prompt: str) -> str:
        self.calls += 1
        self.prompts.append(prompt)
        return self.responses[min(self.calls - 1, len(self.responses) - 1)]


VALID_RISK_RESPONSE = json.dumps(
    {
        "likelihood": "High",
        "impact": "Critical",
        "risk_score": 25,
        "summary": (
            "The risk represents a significant exposure requiring strong"
            " preventive, detective, and governance controls."
        ),
        "recommended_controls": [
            "Strengthen access control enforcement.",
            "Perform recurring control effectiveness reviews.",
            "Maintain supporting evidence for the implemented controls.",
        ],
    }
)


VALID_CONTROL_RESPONSE = json.dumps(
    {
        "overall_assessment": (
            "The existing control posture provides a useful baseline,"
            " while additional safeguards can further reduce the identified risk."
        ),
        "existing_controls_assessment": (
            "The assigned controls address core prevention and detection"
            " requirements, but their evidence and monitoring should remain current."
        ),
        "recommended_existing_controls": [],
        "recommended_new_controls": [
            {
                "control_name": "Enhanced Continuous Control Monitoring",
                "priority": "High",
                "reason": (
                    "Continuous monitoring would improve detection of control"
                    " degradation and support faster remediation of emerging gaps."
                ),
            }
        ],
    }
)


VALID_AUDIT_RESPONSE = json.dumps(
    {
        "overall_assessment": (
            "The audit identified a material issue requiring documented"
            " remediation and continued management oversight."
        ),
        "critical_findings": 999,
        "open_findings": 999,
        "completed_actions": 999,
        "pending_actions": 999,
        "executive_summary": (
            "The audit contains a critical finding and an outstanding"
            " remediation action that require continued attention."
        ),
        "priority_recommendations": [
            "Remediate the critical audit finding.",
            "Track the corrective action through completion.",
        ],
    }
)


def _headers(auth_headers, user):
    return auth_headers(user)


def _json(response):
    assert response.headers["content-type"].startswith("application/json")
    return response.json()


def test_phase53_manager_end_to_end_grc_lifecycle(
    client,
    db,
    users,
    auth_headers,
    monkeypatch,
    tmp_path,
):
    """Create one complete GRC chain and verify all downstream consumers."""

    manager = users["manager"]
    headers = _headers(auth_headers, manager)

    # ---------------------------------------------------------
    # 1. CREATE RISK
    # ---------------------------------------------------------

    risk_response = client.post(
        "/api/v1/risks/",
        headers=headers,
        json={
            "title": "Phase 53 End-to-End Access Risk",
            "description": (
                "A full lifecycle test risk used to validate connected GRC workflows."
            ),
            "likelihood": 5,
            "impact": 5,
            "owner_id": manager.id,
        },
    )

    assert risk_response.status_code == 200
    risk = _json(risk_response)
    risk_id = risk["id"]
    assert risk["risk_score"] == 25

    # ---------------------------------------------------------
    # 2. CREATE CONTROL
    # ---------------------------------------------------------

    control_response = client.post(
        "/api/v1/controls/",
        headers=headers,
        json={
            "title": "Phase 53 Access Review Control",
            "description": (
                "A documented access review control for the end-to-end test."
            ),
            "control_type": "Preventive",
            "status": "Active",
            "effectiveness": 80,
            "owner_id": manager.id,
        },
    )

    assert control_response.status_code == 200
    control = _json(control_response)
    control_id = control["id"]
    assert control["effectiveness"] == 80

    # ---------------------------------------------------------
    # 3. RISK -> CONTROL
    # ---------------------------------------------------------

    risk_control_response = client.post(
        "/api/v1/risk-controls/",
        headers=headers,
        json={
            "risk_id": risk_id,
            "control_id": control_id,
        },
    )

    assert risk_control_response.status_code == 200

    mapped_controls_response = client.get(
        f"/api/v1/risk-controls/risk/{risk_id}",
        headers=headers,
    )

    assert mapped_controls_response.status_code == 200
    mapped_control_ids = {
        item["id"]
        for item in _json(mapped_controls_response)
    }
    assert control_id in mapped_control_ids

    # ---------------------------------------------------------
    # 4. CREATE FRAMEWORK
    # ---------------------------------------------------------

    framework_response = client.post(
        "/api/v1/frameworks/",
        headers=headers,
        json={
            "name": "Phase 53 Test Framework",
            "version": "1.0",
            "description": (
                "Framework created to validate end-to-end compliance traceability."
            ),
        },
    )

    assert framework_response.status_code == 200
    framework = _json(framework_response)
    framework_id = framework["id"]

    # ---------------------------------------------------------
    # 5. CREATE FRAMEWORK REQUIREMENT
    # ---------------------------------------------------------

    framework_control_response = client.post(
        "/api/v1/framework-controls/",
        headers=headers,
        json={
            "framework_id": framework_id,
            "control_code": "P53.1",
            "title": "Periodic Access Review",
            "description": (
                "Organizations must perform and document periodic access reviews."
            ),
        },
    )

    assert framework_control_response.status_code == 200
    framework_control = _json(framework_control_response)
    framework_control_id = framework_control["id"]

    # ---------------------------------------------------------
    # 6. CONTROL -> FRAMEWORK REQUIREMENT
    # ---------------------------------------------------------

    control_framework_response = client.post(
        "/api/v1/control-framework-controls/",
        headers=headers,
        json={
            "control_id": control_id,
            "framework_control_id": framework_control_id,
        },
    )

    assert control_framework_response.status_code == 200

    framework_mappings_response = client.get(
        f"/api/v1/control-framework-controls/control/{control_id}",
        headers=headers,
    )

    assert framework_mappings_response.status_code == 200
    framework_ids = {
        item["id"]
        for item in _json(framework_mappings_response)
    }
    assert framework_control_id in framework_ids

    # ---------------------------------------------------------
    # 7. UPLOAD EVIDENCE
    # ---------------------------------------------------------

    from app.api.v1.routes import evidence as evidence_route

    monkeypatch.setattr(
        evidence_route,
        "UPLOAD_DIR",
        tmp_path,
    )

    evidence_response = client.post(
        "/api/v1/evidence/",
        headers=headers,
        data={
            "control_id": str(control_id),
            "title": "Phase 53 Evidence",
            "description": (
                "Supporting evidence for the Phase 53 control lifecycle."
            ),
        },
        files={
            "file": (
                "phase53-evidence.pdf",
                BytesIO(b"%PDF-1.4 phase53 test evidence"),
                "application/pdf",
            )
        },
    )

    assert evidence_response.status_code == 200
    evidence = _json(evidence_response)
    evidence_id = evidence["id"]
    assert evidence["control_id"] == control_id
    assert evidence["file_name"] == "phase53-evidence.pdf"

    stored_files = list(tmp_path.glob("*"))
    assert len(stored_files) == 1
    assert stored_files[0].suffix == ".pdf"

    # ---------------------------------------------------------
    # 8. CREATE AUDIT
    # ---------------------------------------------------------

    audit_response = client.post(
        "/api/v1/audits/",
        headers=headers,
        json={
            "name": "Phase 53 End-to-End Audit",
            "framework_id": framework_id,
            "auditor_id": manager.id,
            "scope": "GRC Department access governance review",
            "status": "In Progress",
            "start_date": date.today().isoformat(),
            "end_date": (
                date.today() + timedelta(days=30)
            ).isoformat(),
        },
    )

    assert audit_response.status_code == 200
    audit = _json(audit_response)
    audit_id = audit["id"]
    assert audit["framework_id"] == framework_id

    # ---------------------------------------------------------
    # 9. CREATE AUDIT FINDING
    # ---------------------------------------------------------

    finding_response = client.post(
        "/api/v1/audit-findings/",
        headers=headers,
        json={
            "audit_id": audit_id,
            "control_id": control_id,
            "title": "Phase 53 Critical Access Review Finding",
            "description": (
                "Required access review records were not consistently maintained."
            ),
            "severity": "Critical",
            "recommendation": (
                "Implement documented periodic access review records and retain evidence."
            ),
            "status": "Open",
        },
    )

    assert finding_response.status_code == 200
    finding = _json(finding_response)
    finding_id = finding["id"]
    assert finding["audit_id"] == audit_id
    assert finding["control_id"] == control_id

    # ---------------------------------------------------------
    # 10. CREATE OVERDUE CRITICAL CORRECTIVE ACTION
    # ---------------------------------------------------------

    overdue_date = date.today() - timedelta(days=1)

    action_response = client.post(
        "/api/v1/corrective-actions/",
        headers=headers,
        json={
            "finding_id": finding_id,
            "assigned_to": manager.id,
            "title": "Phase 53 Remediate Access Review Finding",
            "description": (
                "Implement the required access review process and supporting records."
            ),
            "priority": "Critical",
            "status": "Open",
            "due_date": overdue_date.isoformat(),
            "comments": "Phase 53 remediation workflow test.",
        },
    )

    assert action_response.status_code == 200
    action = _json(action_response)
    action_id = action["id"]
    assert action["finding_id"] == finding_id
    assert action["priority"] == "Critical"

    # ---------------------------------------------------------
    # 11. VERIFY RISK INTELLIGENCE
    # ---------------------------------------------------------

    intelligence_response = client.get(
        f"/api/v1/intelligence/risk/{risk_id}",
        headers=headers,
    )

    assert intelligence_response.status_code == 200
    intelligence = _json(intelligence_response)
    metrics = intelligence["metrics"]

    assert intelligence["risk_id"] == risk_id
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

    control_graph = intelligence["controls"][0]
    assert control_graph["id"] == control_id
    assert control_graph["evidence"][0]["id"] == evidence_id
    assert control_graph["frameworks"][0]["id"] == framework_control_id
    assert control_graph["findings"][0]["id"] == finding_id
    assert control_graph["findings"][0]["actions"][0]["id"] == action_id

    # ---------------------------------------------------------
    # 12. VERIFY CONTINUOUS MONITORING
    # ---------------------------------------------------------

    monitoring_response = client.get(
        f"/api/v1/monitoring/risk/{risk_id}",
        headers=headers,
    )

    assert monitoring_response.status_code == 200
    monitoring = _json(monitoring_response)

    alert_types = {
        alert["alert_type"]
        for alert in monitoring["alerts"]
    }

    assert "CRITICAL_RISK" in alert_types
    assert "CRITICAL_FINDING" in alert_types
    assert "CRITICAL_ACTION" in alert_types
    assert "OVERDUE_ACTION" in alert_types
    assert "RISK_WITHOUT_CONTROLS" not in alert_types
    assert "CONTROL_WITHOUT_EVIDENCE" not in alert_types

    # ---------------------------------------------------------
    # 13. VERIFY REPORTS
    # ---------------------------------------------------------

    risk_report_response = client.get(
        "/api/v1/reports/risks",
        headers=headers,
    )

    assert risk_report_response.status_code == 200
    risk_report = _json(risk_report_response)
    assert any(
        item["id"] == risk_id
        for item in risk_report["risks"]
    )

    audit_report_response = client.get(
        "/api/v1/reports/audits",
        headers=headers,
    )

    assert audit_report_response.status_code == 200
    audit_report = _json(audit_report_response)
    audit_item = next(
        item
        for item in audit_report["audits"]
        if item["id"] == audit_id
    )
    assert audit_item["finding_count"] == 1
    assert audit_item["critical_finding_count"] == 1
    assert audit_item["open_finding_count"] == 1

    compliance_report_response = client.get(
        "/api/v1/reports/compliance",
        headers=headers,
    )

    assert compliance_report_response.status_code == 200
    compliance_report = _json(compliance_report_response)
    framework_item = next(
        item
        for item in compliance_report["frameworks"]
        if item["id"] == framework_id
    )
    assert framework_item["control_count"] == 1
    assert framework_item["active_control_count"] == 1
    assert framework_item["average_effectiveness"] == 80.0
    assert framework_item["evidence_count"] == 1
    assert framework_item["finding_count"] == 1
    assert framework_item["critical_finding_count"] == 1
    assert framework_item["open_finding_count"] == 1

    # ---------------------------------------------------------
    # 14. VERIFY DASHBOARD
    # ---------------------------------------------------------

    dashboard_response = client.get(
        "/api/v1/dashboard/",
        headers=headers,
    )

    assert dashboard_response.status_code == 200
    dashboard = _json(dashboard_response)
    assert dashboard["totalRisks"] >= 1
    assert dashboard["controls"] >= 1
    assert dashboard["totalEvidence"] >= 1
    assert dashboard["audits"] >= 1
    assert dashboard["totalFindings"] >= 1
    assert dashboard["openFindings"] >= 1
    assert dashboard["criticalFindings"] >= 1
    assert dashboard["totalActions"] >= 1
    assert dashboard["overdueActions"] >= 1

    # ---------------------------------------------------------
    # 15. VERIFY CONTEXTUAL AI WORKFLOWS
    # ---------------------------------------------------------

    from app.services.ai import audit_ai_service
    from app.services.ai import control_ai_service
    from app.services.ai import risk_ai_service

    risk_provider = FakeProvider([VALID_RISK_RESPONSE])
    control_provider = FakeProvider([VALID_CONTROL_RESPONSE])
    audit_provider = FakeProvider([VALID_AUDIT_RESPONSE])

    monkeypatch.setattr(
        risk_ai_service,
        "get_ai_provider",
        lambda: risk_provider,
    )
    monkeypatch.setattr(
        control_ai_service,
        "get_ai_provider",
        lambda: control_provider,
    )
    monkeypatch.setattr(
        audit_ai_service,
        "get_ai_provider",
        lambda: audit_provider,
    )

    risk_ai_response = client.post(
        f"/api/v1/ai/risk/{risk_id}/analyze",
        headers=headers,
    )
    assert risk_ai_response.status_code == 200
    assert _json(risk_ai_response)["risk_score"] == 25
    assert risk_provider.calls == 1

    control_ai_response = client.post(
        f"/api/v1/ai/risk/{risk_id}/recommend-controls",
        headers=headers,
    )
    assert control_ai_response.status_code == 200
    control_ai_body = _json(control_ai_response)
    assert control_ai_body["overall_assessment"]
    assert control_provider.calls == 1

    audit_ai_response = client.post(
        f"/api/v1/ai/audit/{audit_id}/summarize",
        headers=headers,
    )
    assert audit_ai_response.status_code == 200
    audit_ai_body = _json(audit_ai_response)
    assert audit_ai_body["critical_findings"] == 1
    assert audit_ai_body["open_findings"] == 1
    assert audit_ai_body["completed_actions"] == 0
    assert audit_ai_body["pending_actions"] == 1
    assert audit_provider.calls == 1

    # ---------------------------------------------------------
    # FINAL GRAPH ASSERTION
    # ---------------------------------------------------------

    risk_response_after = client.get(
        f"/api/v1/risks/{risk_id}",
        headers=headers,
    )

    assert risk_response_after.status_code == 200
    assert _json(risk_response_after)["id"] == risk_id

    assert evidence_id > 0
    assert action_id > 0
