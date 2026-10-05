"""
AI Explanation Service for Risk Response Workflow Intelligence

Phase 61.9
----------

Provides a read-only AI explanation layer over the deterministic
Risk Response Workflow Intelligence domain.

The AI does NOT:
- calculate workflow intelligence;
- change workflow state;
- change risk state;
- change treatment state;
- execute responses;
- mutate any GRC resource.

The deterministic intelligence service remains authoritative.
AI is only used to explain already-derived intelligence.
"""

from __future__ import annotations

import json

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.ai.governance import (
    AIGovernanceError,
    record_ai_event,
    secure_prompt,
    validate_ai_model,
    validate_raw_response,
)
from app.ai.provider_factory import get_ai_provider
from app.ai.prompts import WORKFLOW_INTELLIGENCE_EXPLANATION_PROMPT
from app.auth.ai_access import get_authorized_risk
from app.models.user import User
from app.schemas.ai import (
    AIWorkflowExplanation,
    WorkflowIntelligenceExplanationResponse,
)
from app.services.governed_response_execution_service import (
    get_response_workflow,
)
from app.services.risk_response_workflow_intelligence_service import (
    get_workflow_intelligence,
)


def _enum_value(value):
    """
    Return the value of an enum-like object.

    Plain strings are returned unchanged.
    None remains None.
    """

    if value is None:
        return None

    return getattr(
        value,
        "value",
        value,
    )


def _build_prompt(
    workflow,
    intelligence,
) -> str:
    """
    Build the AI prompt using authoritative deterministic
    workflow intelligence.
    """

    raw_prompt = WORKFLOW_INTELLIGENCE_EXPLANATION_PROMPT.format(
        status=intelligence.status,
        health=_enum_value(
            intelligence.health
        ),
        age_days=intelligence.age_days,
        attention_required=(
            intelligence.attention_required
        ),
        decision_priority=_enum_value(
            intelligence.decision_priority
        ),
        priority_requires_attention=(
            intelligence.priority_requires_attention
        ),
        bottlenecked=intelligence.bottlenecked,
        bottleneck_reason_codes=[
            _enum_value(reason)
            for reason in intelligence.bottleneck_reason_codes
        ],
        escalation_recommendation=_enum_value(
            intelligence.escalation_recommendation
        ),
        escalation_requires_human_review=(
            intelligence.escalation_requires_human_review
        ),
        escalation_reason_codes=[
            _enum_value(reason)
            for reason in intelligence.escalation_reason_codes
        ],
        dependency_state=_enum_value(
            intelligence.dependency_state
        ),
        dependency_reason_codes=[
            _enum_value(reason)
            for reason in intelligence.dependency_reason_codes
        ],
        dependency_target_type=(
            intelligence.dependency_target_type
        ),
        dependency_target_id=(
            intelligence.dependency_target_id
        ),
        workflow_type=getattr(
            workflow,
            "workflow_type",
            "",
        ),
        workflow_title=getattr(
            workflow,
            "title",
            "",
        ),
        workflow_description=getattr(
            workflow,
            "description",
            "",
        ),
        risk_id=intelligence.risk_id,
    )

    return secure_prompt(
        raw_prompt
    )


def _build_response(
    intelligence,
    ai_payload: dict,
) -> WorkflowIntelligenceExplanationResponse:
    """
    Combine deterministic authoritative state with AI-generated
    explanation fields.

    AI is only allowed to provide:
    - explanation
    - key_drivers
    - review_areas

    All workflow intelligence fields come from the deterministic
    intelligence service.
    """

    ai_result = validate_ai_model(
        ai_payload,
        AIWorkflowExplanation,
    )

    return WorkflowIntelligenceExplanationResponse(
        workflow_id=intelligence.workflow_id,
        risk_id=intelligence.risk_id,
        status=intelligence.status,
        health=_enum_value(
            intelligence.health
        ),
        age_days=intelligence.age_days,
        attention_required=(
            intelligence.attention_required
        ),
        decision_priority=_enum_value(
            intelligence.decision_priority
        ),
        priority_requires_attention=(
            intelligence.priority_requires_attention
        ),
        bottlenecked=intelligence.bottlenecked,
        escalation_recommendation=_enum_value(
            intelligence.escalation_recommendation
        ),
        escalation_requires_human_review=(
            intelligence.escalation_requires_human_review
        ),
        dependency_state=_enum_value(
            intelligence.dependency_state
        ),
        explanation=ai_result.explanation,
        key_drivers=ai_result.key_drivers,
        review_areas=ai_result.review_areas,
    )


def explain_risk_response_workflow(
    db: Session,
    risk_id: int,
    workflow_id: int,
    current_user: User,
) -> WorkflowIntelligenceExplanationResponse:
    """
    Generate an AI explanation for a risk response workflow.

    Security properties:
    - Resource authorization occurs before provider initialization.
    - Workflow lookup is scoped to the authorized risk.
    - Deterministic workflow intelligence remains authoritative.
    - AI only provides explanation content.
    - Invalid AI output receives one controlled retry.
    - Provider failures are translated to generic API errors.
    - No workflow or GRC resource is mutated.
    """

    # ==========================================================
    # RESOURCE AUTHORIZATION
    # ==========================================================

    risk = get_authorized_risk(
        db,
        current_user,
        risk_id,
    )

    if risk is None:
        raise HTTPException(
            status_code=404,
            detail="Risk not found.",
        )

    # ==========================================================
    # RISK-SCOPED WORKFLOW LOOKUP
    # ==========================================================

    workflow = get_response_workflow(
        db,
        workflow_id,
        risk_id,
    )

    if workflow is None:
        raise HTTPException(
            status_code=404,
            detail="Response workflow not found.",
        )

    # ==========================================================
    # DETERMINISTIC WORKFLOW INTELLIGENCE
    # ==========================================================

    intelligence = get_workflow_intelligence(
        workflow
    )

    # ==========================================================
    # BUILD GOVERNED PROMPT
    # ==========================================================

    raw_prompt = WORKFLOW_INTELLIGENCE_EXPLANATION_PROMPT.format(
        status=intelligence.status,
        health=_enum_value(
            intelligence.health
        ),
        age_days=intelligence.age_days,
        attention_required=(
            intelligence.attention_required
        ),
        decision_priority=_enum_value(
            intelligence.decision_priority
        ),
        priority_requires_attention=(
            intelligence.priority_requires_attention
        ),
        bottlenecked=intelligence.bottlenecked,
        bottleneck_reason_codes=[
            _enum_value(reason)
            for reason in intelligence.bottleneck_reason_codes
        ],
        escalation_recommendation=_enum_value(
            intelligence.escalation_recommendation
        ),
        escalation_requires_human_review=(
            intelligence.escalation_requires_human_review
        ),
        escalation_reason_codes=[
            _enum_value(reason)
            for reason in intelligence.escalation_reason_codes
        ],
        dependency_state=_enum_value(
            intelligence.dependency_state
        ),
        dependency_reason_codes=[
            _enum_value(reason)
            for reason in intelligence.dependency_reason_codes
        ],
        dependency_target_type=(
            intelligence.dependency_target_type
        ),
        dependency_target_id=(
            intelligence.dependency_target_id
        ),
        workflow_type=getattr(
            workflow,
            "workflow_type",
            "",
        ),
        workflow_title=getattr(
            workflow,
            "title",
            "",
        ),
        workflow_description=getattr(
            workflow,
            "description",
            "",
        ),
        risk_id=intelligence.risk_id,
    )

    try:
        prompt = secure_prompt(
            raw_prompt
        )

    except AIGovernanceError:
        record_ai_event(
            "workflow_intelligence_explanation",
            model="unknown",
            outcome="rejected",
            validation="prompt",
        )

        raise HTTPException(
            status_code=503,
            detail="AI request could not be processed.",
        )

    # ==========================================================
    # PROVIDER INITIALIZATION
    # ==========================================================

    try:
        provider = get_ai_provider()

    except Exception:
        record_ai_event(
            "workflow_intelligence_explanation",
            model="unknown",
            outcome="failure",
            validation="provider_initialization",
        )

        raise HTTPException(
            status_code=503,
            detail="AI service is temporarily unavailable.",
        )

    model_name = getattr(
        provider,
        "model",
        "unknown",
    )

    # ==========================================================
    # AI GENERATION + GOVERNED VALIDATION
    # ==========================================================

    for attempt in range(2):

        try:
            raw_response = provider.generate(
                prompt
            )

            response = validate_raw_response(
                raw_response
            )

            response_json = json.loads(
                response.strip()
            )

            result = _build_response(
                intelligence,
                response_json,
            )

            record_ai_event(
                "workflow_intelligence_explanation",
                model=model_name,
                outcome="success",
                validation="schema",
            )

            return result

        except AIGovernanceError:

            if attempt == 0:
                prompt += """

IMPORTANT:

Your previous response failed the required
security validation.

Return ONLY valid JSON.

Do NOT include Markdown.

Do NOT include explanations.

Do NOT include additional fields.

Return only the required JSON object.
"""

                continue

            record_ai_event(
                "workflow_intelligence_explanation",
                model=model_name,
                outcome="rejected",
                validation="schema",
            )

            raise HTTPException(
                status_code=502,
                detail="AI returned an invalid response after retry.",
            )

        except json.JSONDecodeError:

            if attempt == 0:
                prompt += """

IMPORTANT:

Your previous response was not valid JSON.

Return ONLY valid JSON.

Do NOT include Markdown.

Do NOT include explanations.

Do NOT include additional fields.

Return only the required JSON object.
"""

                continue

            record_ai_event(
                "workflow_intelligence_explanation",
                model=model_name,
                outcome="rejected",
                validation="json",
            )

            raise HTTPException(
                status_code=502,
                detail="AI returned an invalid response after retry.",
            )

        except Exception:
            record_ai_event(
                "workflow_intelligence_explanation",
                model=model_name,
                outcome="failure",
                validation="provider",
            )

            raise HTTPException(
                status_code=503,
                detail="AI service is temporarily unavailable.",
            )

    raise HTTPException(
        status_code=503,
        detail="AI service is temporarily unavailable.",
    )