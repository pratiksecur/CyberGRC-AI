import json


class FakeProvider:
    def __init__(self, response: str, model: str):
        self.response = response
        self.model = model
        self.calls = 0
        self.prompts = []

    def generate(self, prompt: str) -> str:
        self.calls += 1
        self.prompts.append(prompt)
        return self.response


VALID_RISK_RESPONSE = json.dumps(
    {
        "likelihood": "High",
        "impact": "High",
        "risk_score": 20,
        "summary": (
            "The risk presents a significant exposure that warrants"
            " strengthened preventative and detective controls."
        ),
        "recommended_controls": [
            "Implement stronger access controls.",
            "Enable continuous security monitoring.",
            "Review privileged access regularly.",
        ],
    }
)


VALID_CONTROL_RESPONSE = json.dumps(
    {
        "overall_assessment": (
            "The current control posture provides useful coverage,"
            " but additional safeguards should be considered for the"
            " identified risk."
        ),
        "existing_controls_assessment": (
            "The controls already associated with the risk provide a"
            " baseline, although additional monitoring and governance"
            " measures may strengthen the overall treatment."
        ),
        "recommended_existing_controls": [],
        "recommended_new_controls": [
            {
                "control_name": "Additional Risk Monitoring Control",
                "priority": "High",
                "reason": (
                    "An additional monitoring control would provide"
                    " stronger detection and earlier escalation for"
                    " the identified risk."
                ),
            }
        ],
    }
)


VALID_AUDIT_RESPONSE = json.dumps(
    {
        "overall_assessment": (
            "The audit identified active issues requiring remediation"
            " and continued oversight."
        ),
        "critical_findings": 999,
        "open_findings": 999,
        "completed_actions": 999,
        "pending_actions": 999,
        "executive_summary": (
            "The audit contains findings that require documented"
            " remediation and continued management attention."
        ),
        "priority_recommendations": [
            "Review the highest-priority open audit findings.",
            "Track corrective actions through completion.",
        ],
    }
)


VALID_EXECUTIVE_RESPONSE = json.dumps(
    {
        "organization_risk_level": "Elevated",
        "executive_summary": (
            "The organization should continue focusing management"
            " attention on material risks, control effectiveness,"
            " evidence coverage, and remediation progress."
        ),
        "top_priorities": [
            "Address critical risks.",
            "Improve evidence coverage.",
        ],
        "recommended_next_steps": [
            "Review critical remediation items.",
            "Track corrective action completion.",
        ],
    }
)


def test_phase53_ai_understands_complete_grc_lifecycle(
    client,
    users,
    resource_data,
    auth_headers,
    monkeypatch,
):
    """Verify each contextual AI workflow receives the correct lifecycle context."""

    manager = users["manager"]
    headers = auth_headers(manager)

    risk = resource_data["risks"]["manager"]
    control = resource_data["controls"]["manager"]
    audit = resource_data["audits"]["manager"]
    finding = resource_data["findings"]["manager"]
    action = resource_data["corrective_actions"]["manager"]

    # ---------------------------------------------------------
    # Connect the manager risk to the manager control.
    # ---------------------------------------------------------

    mapping_response = client.post(
        "/api/v1/risk-controls/",
        headers=headers,
        json={
            "risk_id": risk.id,
            "control_id": control.id,
        },
    )

    assert mapping_response.status_code == 200

    # ---------------------------------------------------------
    # RISK AI
    # ---------------------------------------------------------

    from app.services.ai import risk_ai_service

    risk_provider = FakeProvider(
        VALID_RISK_RESPONSE,
        "phase53-risk-model",
    )

    monkeypatch.setattr(
        risk_ai_service,
        "get_ai_provider",
        lambda: risk_provider,
    )

    risk_response = client.post(
        f"/api/v1/ai/risk/{risk.id}/analyze",
        headers=headers,
    )

    assert risk_response.status_code == 200
    assert risk_response.json()["risk_score"] == 20
    assert risk_provider.calls == 1

    risk_prompt = risk_provider.prompts[0]
    assert risk.title in risk_prompt
    assert risk.description in risk_prompt

    # ---------------------------------------------------------
    # CONTROL RECOMMENDATION AI
    # ---------------------------------------------------------

    from app.services.ai import control_ai_service

    control_provider = FakeProvider(
        VALID_CONTROL_RESPONSE,
        "phase53-control-model",
    )

    monkeypatch.setattr(
        control_ai_service,
        "get_ai_provider",
        lambda: control_provider,
    )

    control_response = client.post(
        f"/api/v1/ai/risk/{risk.id}/recommend-controls",
        headers=headers,
    )

    assert control_response.status_code == 200
    assert control_response.json()["overall_assessment"]
    assert control_provider.calls == 1

    control_prompt = control_provider.prompts[0]
    assert risk.title in control_prompt
    assert control.title in control_prompt
    assert control.description in control_prompt
    assert "Admin Control" not in control_prompt

    # ---------------------------------------------------------
    # AUDIT AI
    # ---------------------------------------------------------

    from app.services.ai import audit_ai_service

    audit_provider = FakeProvider(
        VALID_AUDIT_RESPONSE,
        "phase53-audit-model",
    )

    monkeypatch.setattr(
        audit_ai_service,
        "get_ai_provider",
        lambda: audit_provider,
    )

    audit_response = client.post(
        f"/api/v1/ai/audit/{audit.id}/summarize",
        headers=headers,
    )

    assert audit_response.status_code == 200
    audit_body = audit_response.json()

    # Metrics must come from the database, not from the fake AI values.
    assert audit_body["critical_findings"] == 0
    assert audit_body["open_findings"] == 1
    assert audit_body["completed_actions"] == 0
    assert audit_body["pending_actions"] == 1
    assert audit_provider.calls == 1

    audit_prompt = audit_provider.prompts[0]
    assert audit.name in audit_prompt
    assert finding.title in audit_prompt
    assert action.title in audit_prompt

    # ---------------------------------------------------------
    # EXECUTIVE AI
    # ---------------------------------------------------------

    from app.services.ai import executive_dashboard_ai_service

    executive_provider = FakeProvider(
        VALID_EXECUTIVE_RESPONSE,
        "phase53-executive-model",
    )

    monkeypatch.setattr(
        executive_dashboard_ai_service,
        "get_ai_provider",
        lambda: executive_provider,
    )

    executive_response = client.get(
        "/api/v1/ai/dashboard/executive-summary",
        headers=headers,
    )

    assert executive_response.status_code == 200
    executive_body = executive_response.json()
    assert executive_body["organization_risk_level"] == "Elevated"
    assert executive_provider.calls == 1

    executive_prompt = executive_provider.prompts[0]
    assert "Total Risks:" in executive_prompt
    assert "Implemented Controls:" in executive_prompt
    assert "Evidence Records:" in executive_prompt
    assert "Audits:" in executive_prompt
    assert "Pending Corrective Actions:" in executive_prompt
