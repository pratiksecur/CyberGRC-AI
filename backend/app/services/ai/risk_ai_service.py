import json

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

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
    Analyze a risk using AI only after applying the same
    resource-level visibility rules as the GRC API.

    Security properties:
    - Authorization occurs before AI provider initialization.
    - Unauthorized resources never reach the AI provider.
    - Provider initialization failures do not expose internal
      exception details.
    - Provider execution failures do not expose internal
      exception details.
    - AI output is validated before being returned.
    """

    # ==========================================================
    # AUTHORIZATION
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
    # AI PROVIDER INITIALIZATION
    # ==========================================================

    try:
        provider = get_ai_provider()

    except Exception:
        raise HTTPException(
            status_code=503,
            detail=(
                "AI service is temporarily unavailable."
            ),
        )

    # ==========================================================
    # PROMPT
    # ==========================================================

    prompt = RISK_ANALYSIS_PROMPT.format(
        title=risk.title,
        description=risk.description,
    )

    # ==========================================================
    # GENERATE + VALIDATE
    # ==========================================================

    for attempt in range(2):

        try:
            response = provider.generate(
                prompt
            )

            response_json = json.loads(
                response
            )

            return RiskAnalysisResponse(
                **response_json
            )

        except (
            json.JSONDecodeError,
            ValidationError,
        ):

            if attempt == 0:

                prompt += """

IMPORTANT:

Your previous response was invalid.

Return ONLY valid JSON.

Do NOT include markdown.

Do NOT include explanations.

Return only the JSON object.
"""

                continue

            raise HTTPException(
                status_code=502,
                detail=(
                    "AI returned an invalid response "
                    "after retry."
                ),
            )

        except Exception:
            raise HTTPException(
                status_code=503,
                detail=(
                    "AI service is temporarily unavailable."
                ),
            )

    raise HTTPException(
        status_code=503,
        detail=(
            "AI service is temporarily unavailable."
        ),
    )