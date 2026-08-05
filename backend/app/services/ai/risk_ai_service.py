import json

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.provider_factory import get_ai_provider
from app.ai.prompts import RISK_ANALYSIS_PROMPT

from app.schemas.ai import RiskAnalysisResponse

from app.services.risk_service import get_risk_by_id


def analyze_risk(
    db: Session,
    risk_id: int,
) -> RiskAnalysisResponse:
    """
    Analyze an existing cybersecurity risk using AI.
    """

    risk = get_risk_by_id(
        db,
        risk_id,
    )

    if risk is None:
        raise HTTPException(
            status_code=404,
            detail="Risk not found."
        )

    provider = get_ai_provider()

    prompt = RISK_ANALYSIS_PROMPT.format(
        title=risk.title,
        description=risk.description,
    )

    for attempt in range(2):

        response = provider.generate(prompt)

        try:

            response_json = json.loads(response)

            return RiskAnalysisResponse(
                **response_json
            )

        except (json.JSONDecodeError, ValidationError):

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
                detail="AI returned invalid JSON after retry."
            )

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=f"AI analysis failed: {str(e)}"
            )