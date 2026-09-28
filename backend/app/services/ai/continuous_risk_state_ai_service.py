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
from app.ai.prompts import (
    CONTINUOUS_RISK_STATE_EXPLANATION_PROMPT,
)
from app.auth.ai_access import get_authorized_risk
from app.models.user import User
from app.schemas.ai import (
    AIContinuousRiskStateExplanation,
    RiskStateExplanationResponse,
)
from app.services.grc_intelligence_service import (
    get_risk_intelligence,
)


def explain_continuous_risk_state(
    db: Session,
    risk_id: int,
    current_user: User,
) -> RiskStateExplanationResponse:
    """
    Explain an already-determined continuous risk state.

    Security properties:

    - Risk authorization occurs before AI provider initialization.
    - GRC intelligence is generated through the existing
      visibility-aware intelligence layer.
    - The deterministic continuous-risk state remains authoritative.
    - AI receives state and GRC context only for explanation.
    - AI cannot change the risk or treatment state.
    - Provider failures are translated to generic API errors.
    - Raw provider responses are size-checked before parsing.
    - AI output is strictly schema validated.
    - Invalid AI output receives one controlled retry only.
    - Governance events never contain raw prompts/responses.
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
    # VISIBILITY-AWARE GRC CONTEXT
    # ==========================================================

    intelligence = get_risk_intelligence(
        db,
        risk_id,
        current_user,
    )

    if intelligence is None:
        raise HTTPException(
            status_code=404,
            detail="Risk not found.",
        )

    metrics = intelligence.metrics

    # ----------------------------------------------------------
    # Deterministic state
    # ----------------------------------------------------------

    risk_state = metrics.continuous_risk_state
    treatment_state = metrics.treatment_state
    reassessment_required = (
        metrics.reassessment_required
    )

    # ----------------------------------------------------------
    # Deterministic reasons
    #
    # Resource identifiers are intentionally excluded from
    # the AI prompt. The model only needs the authoritative
    # reason code, severity, and explanation.
    # ----------------------------------------------------------

    state_reasons = [
        {
            "code": reason.code,
            "severity": reason.severity,
            "message": reason.message,
        }
        for reason in metrics.state_reasons
    ]

    # ----------------------------------------------------------
    # GRC metrics
    # ----------------------------------------------------------

    grc_metrics = {
        "control_count": metrics.control_count,
        "controls_with_evidence": (
            metrics.controls_with_evidence
        ),
        "evidence_coverage_percent": (
            metrics.evidence_coverage_percent
        ),
        "average_control_effectiveness": (
            metrics.average_control_effectiveness
        ),
        "framework_count": metrics.framework_count,
        "finding_count": metrics.finding_count,
        "open_findings": metrics.open_findings,
        "critical_findings": metrics.critical_findings,
        "action_count": metrics.action_count,
        "open_actions": metrics.open_actions,
        "overdue_actions": metrics.overdue_actions,
        "remediation_completion_percent": (
            metrics.remediation_completion_percent
        ),
        "treatment_count": metrics.treatment_count,
        "effective_treatment_count": (
            metrics.effective_treatment_count
        ),
    }

    # ==========================================================
    # BUILD PROMPT
    # ==========================================================

    raw_prompt = (
        CONTINUOUS_RISK_STATE_EXPLANATION_PROMPT.format(
            risk_state=risk_state,
            treatment_state=treatment_state,
            reassessment_required=(
                str(reassessment_required)
            ),
            risk_score=(
                intelligence.risk_score
            ),
            residual_risk=(
                metrics.estimated_residual_risk
            ),
            control_residual_risk=(
                metrics.control_estimated_residual_risk
            ),
            state_reasons=json.dumps(
                state_reasons,
                ensure_ascii=True,
            ),
            grc_metrics=json.dumps(
                grc_metrics,
                ensure_ascii=True,
            ),
            risk_title=risk.title,
            risk_description=risk.description,
        )
    )

    try:
        prompt = secure_prompt(
            raw_prompt
        )

    except AIGovernanceError:
        record_ai_event(
            "continuous_risk_state_explanation",
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
            "continuous_risk_state_explanation",
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

            result = validate_ai_model(
                response_json,
                AIContinuousRiskStateExplanation,
            )

            record_ai_event(
                "continuous_risk_state_explanation",
                model=model_name,
                outcome="success",
                validation="schema",
            )

            # --------------------------------------------------
            # IMPORTANT:
            #
            # The state returned to the client is NOT taken
            # from the AI response.
            #
            # It comes directly from the deterministic
            # GRC intelligence layer.
            # --------------------------------------------------

            return RiskStateExplanationResponse(
                risk_state=risk_state,
                treatment_state=treatment_state,
                reassessment_required=(
                    reassessment_required
                ),
                explanation=result.explanation,
                key_drivers=result.key_drivers,
                review_areas=result.review_areas,
            )

        except AIGovernanceError:

            if attempt == 0:
                prompt += """

IMPORTANT:

Your previous response failed the required
security validation.

Return ONLY valid JSON.

Do NOT include Markdown.

Do NOT include explanations outside the JSON.

Do NOT add additional fields.

Do NOT change the authoritative risk state,
treatment state, or reassessment requirement.

Return only the required JSON object.
"""

                continue

            record_ai_event(
                "continuous_risk_state_explanation",
                model=model_name,
                outcome="rejected",
                validation="schema",
            )

            raise HTTPException(
                status_code=502,
                detail=(
                    "AI returned an invalid response "
                    "after retry."
                ),
            )

        except json.JSONDecodeError:

            if attempt == 0:
                prompt += """

IMPORTANT:

Your previous response was not valid JSON.

Return ONLY valid JSON.

Do NOT include Markdown.

Do NOT include explanations outside the JSON.

Do NOT add additional fields.

Return only the required JSON object.
"""

                continue

            record_ai_event(
                "continuous_risk_state_explanation",
                model=model_name,
                outcome="rejected",
                validation="json",
            )

            raise HTTPException(
                status_code=502,
                detail=(
                    "AI returned an invalid response "
                    "after retry."
                ),
            )

        except Exception:

            record_ai_event(
                "continuous_risk_state_explanation",
                model=model_name,
                outcome="failure",
                validation="provider",
            )

            raise HTTPException(
                status_code=503,
                detail=(
                    "AI service is temporarily unavailable."
                ),
            )

    raise HTTPException(
        status_code=503,
        detail="AI service is temporarily unavailable.",
    )