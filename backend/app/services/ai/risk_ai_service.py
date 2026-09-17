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
from app.ai.prompts import RISK_ANALYSIS_PROMPT
from app.auth.ai_access import get_authorized_risk
from app.models.user import User
from app.schemas.ai import RiskAnalysisResponse


def analyze_risk(
    db: Session,
    risk_id: int,
    current_user: User,
) -> RiskAnalysisResponse:
    """
    Analyze a risk through the governed AI boundary.

    Security properties:
    - Resource authorization occurs before provider initialization.
    - Unauthorized risks never reach the AI provider.
    - User-controlled GRC text is secured before model invocation.
    - Provider failures are translated to generic API errors.
    - Raw provider responses are size-checked before parsing.
    - Structured AI output is strictly schema validated.
    - Invalid AI output receives one controlled retry only.
    - AI governance events never contain raw prompts/responses.
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
    # BUILD PROMPT
    # ==========================================================

    raw_prompt = RISK_ANALYSIS_PROMPT.format(
        title=risk.title,
        description=risk.description,
    )

    try:
        prompt = secure_prompt(raw_prompt)

    except AIGovernanceError:
        record_ai_event(
            "risk_analysis",
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
            "risk_analysis",
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
                RiskAnalysisResponse,
            )

            record_ai_event(
                "risk_analysis",
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

Do NOT include markdown.

Do NOT include explanations.

Do NOT include additional fields.

Return only the required JSON object.
"""
                continue

            record_ai_event(
                "risk_analysis",
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

Do NOT include markdown.

Do NOT include explanations.

Do NOT include additional fields.

Return only the required JSON object.
"""
                continue

            record_ai_event(
                "risk_analysis",
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
                "risk_analysis",
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