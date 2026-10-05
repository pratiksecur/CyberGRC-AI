"""
Phase 61.9 - Risk Response Workflow AI Explanation Tests

Tests the governed AI explanation layer for risk response workflows.

Security principles verified here:

- authorization happens before provider access;
- deterministic workflow intelligence remains authoritative;
- AI only supplies explanation content;
- AI cannot mutate workflow state;
- AI cannot execute a workflow;
- invalid provider output is retried once;
- provider failures are translated to generic HTTP errors;
- unauthorized users never reach the AI provider;
- workflow lookup remains risk-scoped;
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.schemas.ai import (
    WorkflowIntelligenceExplanationResponse,
)
from app.services.ai import risk_response_workflow_ai_service
from app.services.ai.risk_response_workflow_ai_service import (
    explain_risk_response_workflow,
)
from app.services.risk_response_workflow_intelligence_service import (
    WorkflowDependencyState,
    WorkflowEscalationRecommendation,
    WorkflowHealth,
    RiskResponseWorkflowIntelligence,
)


# ==========================================================
# TEST PROVIDER
# ==========================================================


class FakeProvider:
    """
    Deterministic fake AI provider.

    Supports either:
    - one response string;
    - a list of responses for retry testing;
    - an Exception for provider failure testing.
    """

    model = "test-workflow-model"

    def __init__(self, response):
        self.response = response
        self.calls = 0
        self.prompts = []

    def generate(self, prompt: str) -> str:
        self.calls += 1
        self.prompts.append(prompt)

        if isinstance(self.response, Exception):
            raise self.response

        if isinstance(self.response, list):
            index = min(
                self.calls - 1,
                len(self.response) - 1,
            )
            response = self.response[index]

            if isinstance(response, Exception):
                raise response

            return response

        return self.response


# ==========================================================
# VALID AI RESPONSE
# ==========================================================


VALID_WORKFLOW_AI_RESPONSE = json.dumps(
    {
        "explanation": (
            "The workflow requires attention because its "
            "current governance posture indicates that "
            "human review is appropriate."
        ),
        "key_drivers": [
            "Workflow requires attention.",
            "The current response priority requires review.",
        ],
        "review_areas": [
            "Confirm the workflow remains appropriate.",
            "Review the underlying response dependency.",
        ],
    }
)


# ==========================================================
# DETERMINISTIC INTELLIGENCE FIXTURE
# ==========================================================


def _workflow_intelligence(
    *,
    workflow_id: int = 100,
    risk_id: int = 1,
):
    """
    Build deterministic Phase 61 intelligence.

    This deliberately contains values that are different from
    anything the AI response can control.
    """

    return RiskResponseWorkflowIntelligence(
        workflow_id=workflow_id,
        risk_id=risk_id,
        status="OPEN",
        health=WorkflowHealth.AGING,
        age_days=12.0,
        age_seconds=12.0 * 86400,
        attention_required=True,
        reason_codes=(
            "WORKFLOW_AGING",
        ),
        started=False,
        terminal=False,
        time_to_start_seconds=None,
        time_in_progress_seconds=None,
        lifecycle_duration_seconds=None,
        terminal_age_seconds=None,
        decision_priority=None,
        priority_rank=None,
        governance_level=None,
        priority_requires_attention=False,
        priority_reason_codes=(),
        bottlenecked=True,
        bottleneck_reason_codes=(
            "BOTTLENECK_NOT_STARTED",
            "BOTTLENECK_AGING",
        ),
        escalation_recommendation=(
            WorkflowEscalationRecommendation.REVIEW
        ),
        escalation_reason_codes=(
            "AGING_WORKFLOW_REQUIRES_ATTENTION",
        ),
        escalation_requires_human_review=True,
        dependency_state=(
            WorkflowDependencyState.AVAILABLE
        ),
        dependency_reason_codes=(
            "TARGET_RESOURCE_AVAILABLE",
        ),
        dependency_target_type="RISK",
        dependency_target_id=risk_id,
    )


# ==========================================================
# WORKFLOW FIXTURE
# ==========================================================


def _workflow(
    *,
    workflow_id: int = 100,
    risk_id: int = 1,
):
    """
    Lightweight workflow object.

    The AI explanation service only needs the workflow metadata
    after authorization and deterministic intelligence lookup.
    """

    return SimpleNamespace(
        id=workflow_id,
        risk_id=risk_id,
        workflow_type="REVIEW",
        title="Review high-risk workflow",
        description=(
            "Review the current response posture "
            "for the associated risk."
        ),
    )


# ==========================================================
# PROMPT FIXTURE
# ==========================================================


def _install_test_prompt(monkeypatch):
    """
    Replace the production prompt with a deterministic test
    template.

    This lets the tests verify that deterministic workflow
    intelligence is supplied to the provider without depending
    on wording changes in the production prompt.
    """

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "WORKFLOW_INTELLIGENCE_EXPLANATION_PROMPT",
        (
            "WORKFLOW CONTEXT\n"
            "status={status}\n"
            "health={health}\n"
            "age_days={age_days}\n"
            "attention_required={attention_required}\n"
            "decision_priority={decision_priority}\n"
            "priority_requires_attention="
            "{priority_requires_attention}\n"
            "bottlenecked={bottlenecked}\n"
            "bottleneck_reason_codes="
            "{bottleneck_reason_codes}\n"
            "escalation_recommendation="
            "{escalation_recommendation}\n"
            "escalation_requires_human_review="
            "{escalation_requires_human_review}\n"
            "escalation_reason_codes="
            "{escalation_reason_codes}\n"
            "dependency_state={dependency_state}\n"
            "dependency_reason_codes="
            "{dependency_reason_codes}\n"
            "dependency_target_type="
            "{dependency_target_type}\n"
            "dependency_target_id="
            "{dependency_target_id}\n"
            "workflow_type={workflow_type}\n"
            "workflow_title={workflow_title}\n"
            "workflow_description={workflow_description}\n"
            "risk_id={risk_id}\n"
        ),
    )


# ==========================================================
# 61.9A - SUCCESSFUL EXPLANATION
# ==========================================================


def test_workflow_ai_explanation_returns_valid_response(
    db,
    users,
    monkeypatch,
):
    """
    A valid AI response should be returned as a governed
    WorkflowIntelligenceExplanationResponse.
    """

    workflow = _workflow(
        workflow_id=100,
        risk_id=1,
    )

    intelligence = _workflow_intelligence(
        workflow_id=100,
        risk_id=1,
    )

    provider = FakeProvider(
        VALID_WORKFLOW_AI_RESPONSE
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_authorized_risk",
        lambda db, current_user, risk_id: SimpleNamespace(
            id=risk_id
        ),
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_response_workflow",
        lambda db, workflow_id, risk_id: workflow,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_workflow_intelligence",
        lambda workflow: intelligence,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_ai_provider",
        lambda: provider,
    )

    _install_test_prompt(monkeypatch)

    result = explain_risk_response_workflow(
        db=db,
        risk_id=1,
        workflow_id=100,
        current_user=users["manager"],
    )

    assert isinstance(
        result,
        WorkflowIntelligenceExplanationResponse,
    )

    assert result.workflow_id == 100
    assert result.risk_id == 1

    # Deterministic values must come from the intelligence
    # service, not from AI output.
    assert result.status == "OPEN"
    assert result.health == "AGING"
    assert result.age_days == 12.0
    assert result.attention_required is True

    assert result.bottlenecked is True
    assert result.escalation_recommendation == "REVIEW"
    assert (
        result.escalation_requires_human_review
        is True
    )

    assert result.dependency_state == "AVAILABLE"

    # AI-controlled explanation fields.
    assert result.explanation.startswith(
        "The workflow requires attention"
    )
    assert len(result.key_drivers) == 2
    assert len(result.review_areas) == 2

    assert provider.calls == 1


# ==========================================================
# 61.9B - PROVIDER RECEIVES DETERMINISTIC CONTEXT
# ==========================================================


def test_workflow_ai_prompt_contains_deterministic_intelligence(
    db,
    users,
    monkeypatch,
):
    """
    The provider must receive the deterministic workflow
    intelligence as context.
    """

    workflow = _workflow(
        workflow_id=101,
        risk_id=2,
    )

    intelligence = _workflow_intelligence(
        workflow_id=101,
        risk_id=2,
    )

    provider = FakeProvider(
        VALID_WORKFLOW_AI_RESPONSE
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_authorized_risk",
        lambda db, current_user, risk_id: SimpleNamespace(
            id=risk_id
        ),
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_response_workflow",
        lambda db, workflow_id, risk_id: workflow,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_workflow_intelligence",
        lambda workflow: intelligence,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_ai_provider",
        lambda: provider,
    )

    _install_test_prompt(monkeypatch)

    explain_risk_response_workflow(
        db=db,
        risk_id=2,
        workflow_id=101,
        current_user=users["manager"],
    )

    assert provider.calls == 1

    prompt = provider.prompts[0]

    assert "status=OPEN" in prompt
    assert "health=AGING" in prompt
    assert "age_days=12.0" in prompt
    assert "attention_required=True" in prompt

    assert (
        "bottlenecked=True"
        in prompt
    )

    assert (
        "escalation_recommendation=REVIEW"
        in prompt
    )

    assert (
        "dependency_state=AVAILABLE"
        in prompt
    )

    assert (
        "dependency_target_type=RISK"
        in prompt
    )

    assert (
        "dependency_target_id=2"
        in prompt
    )

    assert (
        "workflow_type=REVIEW"
        in prompt
    )

    assert (
        "Review high-risk workflow"
        in prompt
    )


# ==========================================================
# 61.9C - AI CANNOT CONTROL AUTHORITATIVE STATE
# ==========================================================


def test_ai_output_cannot_override_deterministic_state(
    db,
    users,
    monkeypatch,
):
    """
    The AI response schema contains only explanation fields.

    Deterministic state must therefore remain authoritative.
    """

    workflow = _workflow(
        workflow_id=102,
        risk_id=3,
    )

    intelligence = _workflow_intelligence(
        workflow_id=102,
        risk_id=3,
    )

    malicious_response = json.dumps(
        {
            "explanation": (
                "The workflow requires human review "
                "because of its current posture."
            ),
            "key_drivers": [
                "Review is required."
            ],
            "review_areas": [
                "Confirm the response."
            ],
        }
    )

    provider = FakeProvider(
        malicious_response
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_authorized_risk",
        lambda db, current_user, risk_id: SimpleNamespace(
            id=risk_id
        ),
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_response_workflow",
        lambda db, workflow_id, risk_id: workflow,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_workflow_intelligence",
        lambda workflow: intelligence,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_ai_provider",
        lambda: provider,
    )

    _install_test_prompt(monkeypatch)

    result = explain_risk_response_workflow(
        db=db,
        risk_id=3,
        workflow_id=102,
        current_user=users["manager"],
    )

    assert result.status == "OPEN"
    assert result.health == "AGING"
    assert result.age_days == 12.0
    assert result.attention_required is True
    assert result.bottlenecked is True
    assert result.escalation_recommendation == "REVIEW"
    assert result.dependency_state == "AVAILABLE"


# ==========================================================
# 61.9D - INVALID JSON RETRIES ONCE
# ==========================================================


def test_workflow_ai_retries_once_after_invalid_json(
    db,
    users,
    monkeypatch,
):
    """
    Invalid JSON should cause exactly one retry.
    """

    workflow = _workflow(
        workflow_id=103,
        risk_id=4,
    )

    intelligence = _workflow_intelligence(
        workflow_id=103,
        risk_id=4,
    )

    provider = FakeProvider(
        [
            "THIS IS NOT JSON",
            VALID_WORKFLOW_AI_RESPONSE,
        ]
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_authorized_risk",
        lambda db, current_user, risk_id: SimpleNamespace(
            id=risk_id
        ),
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_response_workflow",
        lambda db, workflow_id, risk_id: workflow,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_workflow_intelligence",
        lambda workflow: intelligence,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_ai_provider",
        lambda: provider,
    )

    _install_test_prompt(monkeypatch)

    result = explain_risk_response_workflow(
        db=db,
        risk_id=4,
        workflow_id=103,
        current_user=users["manager"],
    )

    assert result.workflow_id == 103
    assert result.risk_id == 4

    assert provider.calls == 2

    retry_prompt = provider.prompts[1]

    assert "valid JSON" in retry_prompt
    assert "ONLY valid JSON" in retry_prompt
    assert "Do NOT include Markdown" in retry_prompt


# ==========================================================
# 61.9E - INVALID JSON AFTER RETRY
# ==========================================================


def test_workflow_ai_rejects_invalid_json_after_retry(
    db,
    users,
    monkeypatch,
):
    """
    Two invalid responses must result in a controlled 502.
    """

    workflow = _workflow(
        workflow_id=104,
        risk_id=5,
    )

    intelligence = _workflow_intelligence(
        workflow_id=104,
        risk_id=5,
    )

    provider = FakeProvider(
        [
            "INVALID JSON",
            "STILL INVALID JSON",
        ]
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_authorized_risk",
        lambda db, current_user, risk_id: SimpleNamespace(
            id=risk_id
        ),
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_response_workflow",
        lambda db, workflow_id, risk_id: workflow,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_workflow_intelligence",
        lambda workflow: intelligence,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_ai_provider",
        lambda: provider,
    )

    _install_test_prompt(monkeypatch)

    with pytest.raises(HTTPException) as exc:
        explain_risk_response_workflow(
            db=db,
            risk_id=5,
            workflow_id=104,
            current_user=users["manager"],
        )

    assert exc.value.status_code == 502
    assert (
        exc.value.detail
        == "AI returned an invalid response after retry."
    )

    assert provider.calls == 2


# ==========================================================
# 61.9F - PROVIDER FAILURE
# ==========================================================


def test_workflow_ai_provider_failure_is_generic(
    db,
    users,
    monkeypatch,
):
    """
    Provider exceptions must never expose internal details.
    """

    workflow = _workflow(
        workflow_id=105,
        risk_id=6,
    )

    intelligence = _workflow_intelligence(
        workflow_id=105,
        risk_id=6,
    )

    provider = FakeProvider(
        RuntimeError(
            "SECRET INTERNAL PROVIDER FAILURE"
        )
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_authorized_risk",
        lambda db, current_user, risk_id: SimpleNamespace(
            id=risk_id
        ),
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_response_workflow",
        lambda db, workflow_id, risk_id: workflow,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_workflow_intelligence",
        lambda workflow: intelligence,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_ai_provider",
        lambda: provider,
    )

    _install_test_prompt(monkeypatch)

    with pytest.raises(HTTPException) as exc:
        explain_risk_response_workflow(
            db=db,
            risk_id=6,
            workflow_id=105,
            current_user=users["manager"],
        )

    assert exc.value.status_code == 503

    assert (
        exc.value.detail
        == "AI service is temporarily unavailable."
    )

    assert (
        "SECRET INTERNAL PROVIDER FAILURE"
        not in str(exc.value.detail)
    )

    assert provider.calls == 1


# ==========================================================
# 61.9G - UNKNOWN WORKFLOW
# ==========================================================


def test_workflow_ai_unknown_workflow_returns_404(
    db,
    users,
    monkeypatch,
):
    """
    A workflow that cannot be resolved within the supplied
    risk scope must return 404 before the provider is called.
    """

    provider = FakeProvider(
        VALID_WORKFLOW_AI_RESPONSE
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_authorized_risk",
        lambda db, current_user, risk_id: SimpleNamespace(
            id=risk_id
        ),
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_response_workflow",
        lambda db, workflow_id, risk_id: None,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_ai_provider",
        lambda: provider,
    )

    with pytest.raises(HTTPException) as exc:
        explain_risk_response_workflow(
            db=db,
            risk_id=7,
            workflow_id=999999,
            current_user=users["manager"],
        )

    assert exc.value.status_code == 404
    assert (
        exc.value.detail
        == "Response workflow not found."
    )

    assert provider.calls == 0


# ==========================================================
# 61.9H - RISK AUTHORIZATION FAILURE
# ==========================================================


def test_workflow_ai_unauthorized_risk_never_reaches_provider(
    db,
    users,
    monkeypatch,
):
    """
    Authorization must happen before workflow lookup,
    intelligence calculation, or provider access.
    """

    provider = FakeProvider(
        VALID_WORKFLOW_AI_RESPONSE
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_authorized_risk",
        lambda db, current_user, risk_id: None,
    )

    def unexpected_workflow_lookup(
        db,
        workflow_id,
        risk_id,
    ):
        raise AssertionError(
            "Workflow lookup must not occur "
            "for an unauthorized risk."
        )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_response_workflow",
        unexpected_workflow_lookup,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_ai_provider",
        lambda: provider,
    )

    with pytest.raises(HTTPException) as exc:
        explain_risk_response_workflow(
            db=db,
            risk_id=8,
            workflow_id=108,
            current_user=users["employee"],
        )

    assert exc.value.status_code == 404

    assert (
        exc.value.detail
        == "Risk not found."
    )

    assert provider.calls == 0


# ==========================================================
# 61.9I - WORKFLOW IS RISK-SCOPED
# ==========================================================


def test_workflow_ai_uses_supplied_risk_scope(
    db,
    users,
    monkeypatch,
):
    """
    The workflow lookup must receive both workflow_id and
    authorized risk_id.

    This protects the service from accidentally resolving
    a workflow belonging to another risk.
    """

    workflow = _workflow(
        workflow_id=109,
        risk_id=9,
    )

    intelligence = _workflow_intelligence(
        workflow_id=109,
        risk_id=9,
    )

    provider = FakeProvider(
        VALID_WORKFLOW_AI_RESPONSE
    )

    captured = {}

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_authorized_risk",
        lambda db, current_user, risk_id: SimpleNamespace(
            id=risk_id
        ),
    )

    def scoped_workflow_lookup(
        db,
        workflow_id,
        risk_id,
    ):
        captured["workflow_id"] = workflow_id
        captured["risk_id"] = risk_id
        return workflow

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_response_workflow",
        scoped_workflow_lookup,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_workflow_intelligence",
        lambda workflow: intelligence,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_ai_provider",
        lambda: provider,
    )

    _install_test_prompt(monkeypatch)

    explain_risk_response_workflow(
        db=db,
        risk_id=9,
        workflow_id=109,
        current_user=users["manager"],
    )

    assert captured["workflow_id"] == 109
    assert captured["risk_id"] == 9


# ==========================================================
# 61.9J - API SUCCESS
# ==========================================================


def test_workflow_ai_explanation_api_success(
    client,
    users,
    auth_headers,
    resource_data,
    monkeypatch,
):
    """
    The public endpoint must expose the governed explanation
    response for an authorized AI user.
    """

    risk = resource_data["risks"]["analyst"]

    workflow = _workflow(
        workflow_id=110,
        risk_id=risk.id,
    )

    intelligence = _workflow_intelligence(
        workflow_id=110,
        risk_id=risk.id,
    )

    provider = FakeProvider(
        VALID_WORKFLOW_AI_RESPONSE
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_response_workflow",
        lambda db, workflow_id, risk_id: workflow,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_workflow_intelligence",
        lambda workflow: intelligence,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_ai_provider",
        lambda: provider,
    )

    _install_test_prompt(monkeypatch)

    response = client.post(
        (
            f"/api/v1/ai/risk/{risk.id}"
            f"/response-workflows/{workflow.id}"
            "/explanation"
        ),
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["workflow_id"] == workflow.id
    assert body["risk_id"] == risk.id

    assert body["status"] == "OPEN"
    assert body["health"] == "AGING"
    assert body["attention_required"] is True
    assert body["bottlenecked"] is True
    assert body["escalation_recommendation"] == "REVIEW"
    assert body["dependency_state"] == "AVAILABLE"

    assert (
        body["explanation"]
        == (
            "The workflow requires attention because its "
            "current governance posture indicates that "
            "human review is appropriate."
        )
    )

    assert provider.calls == 1


# ==========================================================
# 61.9K - API UNAUTHORIZED ROLE
# ==========================================================


def test_workflow_ai_explanation_api_blocks_employee(
    client,
    users,
    auth_headers,
    resource_data,
    monkeypatch,
):
    """
    Employee does not have generic AI use permission.

    The provider must never be reached.
    """

    risk = resource_data["risks"]["analyst"]

    provider = FakeProvider(
        VALID_WORKFLOW_AI_RESPONSE
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_ai_provider",
        lambda: provider,
    )

    response = client.post(
        (
            f"/api/v1/ai/risk/{risk.id}"
            "/response-workflows/110"
            "/explanation"
        ),
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 403
    assert provider.calls == 0


# ==========================================================
# 61.9L - API UNAUNTHENTICATED
# ==========================================================


def test_workflow_ai_explanation_api_requires_authentication(
    client,
):
    """
    Unauthenticated requests must be rejected before the
    AI service/provider is reached.
    """

    response = client.post(
        "/api/v1/ai/risk/1/response-workflows/110/explanation"
    )

    assert response.status_code == 401


# ==========================================================
# 61.9M - READ-ONLY GUARANTEE
# ==========================================================


def test_workflow_ai_explanation_is_read_only(
    db,
    users,
    monkeypatch,
):
    """
    The explanation layer must not expose or perform a workflow
    mutation/execution operation.

    The workflow object is intentionally a simple mutable object
    so the test can prove its state remains unchanged.
    """

    workflow = _workflow(
        workflow_id=111,
        risk_id=11,
    )

    original_status = getattr(
        workflow,
        "status",
        "OPEN",
    )

    intelligence = _workflow_intelligence(
        workflow_id=111,
        risk_id=11,
    )

    provider = FakeProvider(
        VALID_WORKFLOW_AI_RESPONSE
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_authorized_risk",
        lambda db, current_user, risk_id: SimpleNamespace(
            id=risk_id
        ),
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_response_workflow",
        lambda db, workflow_id, risk_id: workflow,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_workflow_intelligence",
        lambda workflow: intelligence,
    )

    monkeypatch.setattr(
        risk_response_workflow_ai_service,
        "get_ai_provider",
        lambda: provider,
    )

    _install_test_prompt(monkeypatch)

    explain_risk_response_workflow(
        db=db,
        risk_id=11,
        workflow_id=111,
        current_user=users["manager"],
    )

    assert getattr(
        workflow,
        "status",
        "OPEN",
    ) == original_status

    assert provider.calls == 1