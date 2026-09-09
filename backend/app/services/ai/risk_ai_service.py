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
    """

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

    provider = get_ai_provider()

    prompt = RISK_ANALYSIS_PROMPT.format(
        title=risk.title,
        description=risk.description,
    )

    for attempt in range(2):

        response = provider.generate(
            prompt
        )

        try:

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
                status_code=500,
                detail=(
                    "AI returned invalid JSON "
                    "after retry."
                ),
            )

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=(
                    f"AI analysis failed: {str(e)}"
                ),
            )