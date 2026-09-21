import json

import pytest


class FakeProvider:
    def __init__(self, response: str):
        self.response = response
        self.calls = 0
        self.prompts = []
        self.model = "phase51-test-model"

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


VALID_CONTROL_RECOMMENDATION_RESPONSE = json.dumps(
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


def install_provider(monkeypatch, module, provider):
    monkeypatch.setattr(
        module,
        "get_ai_provider",
        lambda: provider,
    )


# ==========================================================
# CONTEXTUAL RISK AI
# ==========================================================


def test_risk_ai_authorized_manager_returns_analysis(
    client,
    users,
    resource_data,
    auth_headers,
    monkeypatch,
):
    from app.services.ai import risk_ai_service

    provider = FakeProvider(VALID_RISK_RESPONSE)
    install_provider(monkeypatch, risk_ai_service, provider)

    risk = resource_data["risks"]["analyst"]

    response = client.post(
        f"/api/v1/ai/risk/{risk.id}/analyze",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["likelihood"] == "High"
    assert body["impact"] == "High"
    assert body["risk_score"] == 20
    assert provider.calls == 1


def test_risk_ai_out_of_scope_manager_returns_404_without_provider(
    client,
    users,
    resource_data,
    auth_headers,
    monkeypatch,
):
    from app.services.ai import risk_ai_service

    provider = FakeProvider(VALID_RISK_RESPONSE)
    install_provider(monkeypatch, risk_ai_service, provider)

    admin_risk = resource_data["risks"]["admin"]

    response = client.post(
        f"/api/v1/ai/risk/{admin_risk.id}/analyze",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 404
    assert provider.calls == 0


def test_risk_control_recommendation_authorized_manager_returns_result(
    client,
    users,
    resource_data,
    auth_headers,
    monkeypatch,
):
    from app.services.ai import control_ai_service

    provider = FakeProvider(
        VALID_CONTROL_RECOMMENDATION_RESPONSE
    )
    install_provider(monkeypatch, control_ai_service, provider)

    risk = resource_data["risks"]["analyst"]

    response = client.post(
        f"/api/v1/ai/risk/{risk.id}/recommend-controls",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["overall_assessment"]
    assert body["existing_controls_assessment"]
    assert len(body["recommended_new_controls"]) == 1
    assert provider.calls == 1

    prompt = provider.prompts[0]

    # GRC Manager AI context must exclude the Admin-owned control
    # while retaining controls inside the manager's visibility scope.
    assert "Admin Control" not in prompt
    assert "Analyst Control" in prompt


def test_risk_control_recommendation_out_of_scope_manager_returns_404(
    client,
    users,
    resource_data,
    auth_headers,
    monkeypatch,
):
    from app.services.ai import control_ai_service

    provider = FakeProvider(
        VALID_CONTROL_RECOMMENDATION_RESPONSE
    )
    install_provider(monkeypatch, control_ai_service, provider)

    admin_risk = resource_data["risks"]["admin"]

    response = client.post(
        f"/api/v1/ai/risk/{admin_risk.id}/recommend-controls",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 404
    assert provider.calls == 0


# ==========================================================
# CONTEXTUAL AUDIT AI
# ==========================================================


def test_audit_ai_authorized_manager_returns_summary_with_authoritative_metrics(
    client,
    users,
    resource_data,
    auth_headers,
    monkeypatch,
):
    from app.services.ai import audit_ai_service

    provider = FakeProvider(VALID_AUDIT_RESPONSE)
    install_provider(monkeypatch, audit_ai_service, provider)

    audit = resource_data["audits"]["manager"]

    response = client.post(
        f"/api/v1/ai/audit/{audit.id}/summarize",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    body = response.json()

    # The service must derive these from the database rather than
    # trusting the model's deliberately incorrect values above.
    assert body["critical_findings"] == 0
    assert body["open_findings"] == 1
    assert body["completed_actions"] == 0
    assert body["pending_actions"] == 1
    assert body["overall_assessment"]
    assert provider.calls == 1


def test_audit_ai_out_of_scope_manager_returns_404_without_provider(
    client,
    users,
    resource_data,
    auth_headers,
    monkeypatch,
):
    from app.services.ai import audit_ai_service

    provider = FakeProvider(VALID_AUDIT_RESPONSE)
    install_provider(monkeypatch, audit_ai_service, provider)

    admin_audit = resource_data["audits"]["admin"]

    response = client.post(
        f"/api/v1/ai/audit/{admin_audit.id}/summarize",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 404
    assert provider.calls == 0


# ==========================================================
# EXECUTIVE AI
# ==========================================================


def test_executive_ai_is_available_to_grc_manager(
    client,
    users,
    auth_headers,
    monkeypatch,
):
    from app.services.ai import executive_dashboard_ai_service

    provider = FakeProvider(VALID_EXECUTIVE_RESPONSE)
    install_provider(
        monkeypatch,
        executive_dashboard_ai_service,
        provider,
    )

    response = client.get(
        "/api/v1/ai/dashboard/executive-summary",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["organization_risk_level"] == "Elevated"
    assert body["executive_summary"]
    assert provider.calls == 1


@pytest.mark.parametrize(
    "user_key",
    [
        "admin",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_executive_ai_is_denied_to_non_manager_roles(
    client,
    users,
    auth_headers,
    user_key,
    monkeypatch,
):
    from app.services.ai import executive_dashboard_ai_service

    provider = FakeProvider(VALID_EXECUTIVE_RESPONSE)
    install_provider(
        monkeypatch,
        executive_dashboard_ai_service,
        provider,
    )

    response = client.get(
        "/api/v1/ai/dashboard/executive-summary",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 403
    assert provider.calls == 0


# ==========================================================
# GENERIC AI ROLE BOUNDARY
# ==========================================================


@pytest.mark.parametrize(
    "user_key",
    [
        "admin",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_generic_risk_ai_respects_role_permission_boundary(
    client,
    users,
    resource_data,
    auth_headers,
    user_key,
    monkeypatch,
):
    from app.services.ai import risk_ai_service

    provider = FakeProvider(VALID_RISK_RESPONSE)
    install_provider(monkeypatch, risk_ai_service, provider)

    # Employee and Risk Analyst do not have generic AI permission.
    # Admin and Auditor do have it, so use each role's own scope-safe
    # risk rather than forcing an authorization failure for those roles.
    risk_key = {
        "admin": "admin",
        "analyst": "analyst",
        "auditor": "auditor",
        "employee": "employee",
    }[user_key]

    risk = resource_data["risks"][risk_key]

    response = client.post(
        f"/api/v1/ai/risk/{risk.id}/analyze",
        headers=auth_headers(users[user_key]),
    )

    if user_key in {"admin", "auditor"}:
        assert response.status_code == 200
        assert provider.calls == 1
    else:
        assert response.status_code == 403
        assert provider.calls == 0


# ==========================================================
# AUDITOR ORGANIZATION-WIDE GENERIC AI ACCESS
# ==========================================================


def test_auditor_can_use_risk_ai_within_organization_scope(
    client,
    users,
    resource_data,
    auth_headers,
    monkeypatch,
):
    from app.services.ai import risk_ai_service

    provider = FakeProvider(VALID_RISK_RESPONSE)
    install_provider(monkeypatch, risk_ai_service, provider)

    admin_risk = resource_data["risks"]["admin"]

    response = client.post(
        f"/api/v1/ai/risk/{admin_risk.id}/analyze",
        headers=auth_headers(users["auditor"]),
    )

    assert response.status_code == 200
    assert provider.calls == 1


def test_auditor_can_use_audit_ai_for_assigned_audit(
    client,
    users,
    resource_data,
    auth_headers,
    monkeypatch,
):
    from app.services.ai import audit_ai_service

    provider = FakeProvider(VALID_AUDIT_RESPONSE)
    install_provider(monkeypatch, audit_ai_service, provider)

    # Auditor audit visibility is intentionally OWN.
    # Therefore the auditor may use Audit AI for an audit assigned
    # to the auditor, but must not access another user's audit.
    auditor_audit = resource_data["audits"]["auditor"]

    response = client.post(
        f"/api/v1/ai/audit/{auditor_audit.id}/summarize",
        headers=auth_headers(users["auditor"]),
    )

    assert response.status_code == 200
    assert provider.calls == 1


# ==========================================================
# AUTHENTICATION BOUNDARY
# ==========================================================


@pytest.mark.parametrize(
    "method,path",
    [
        ("post", "/api/v1/ai/risk/1/analyze"),
        ("post", "/api/v1/ai/risk/1/recommend-controls"),
        ("post", "/api/v1/ai/audit/1/summarize"),
        ("get", "/api/v1/ai/dashboard/executive-summary"),
    ],
)
def test_ai_endpoints_require_authentication(
    client,
    method,
    path,
):
    response = getattr(client, method)(path)

    assert response.status_code == 401
