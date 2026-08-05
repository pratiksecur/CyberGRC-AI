import json

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.provider_factory import get_ai_provider
from app.ai.prompts import CONTROL_RECOMMENDATION_PROMPT

from app.schemas.ai import (
    ControlRecommendationResponse,
)

from app.services.risk_service import (
    get_risk_by_id,
)

from app.services.risk_control_service import (
    get_controls_for_risk,
)

from app.services.control_service import (
    get_all_controls,
)

from app.services.ai.control_matcher import (
    match_control,
)


def recommend_controls(
    db: Session,
    risk_id: int,
) -> ControlRecommendationResponse:
    """
    Generate AI recommendations based on:
    - Risk
    - Existing assigned controls
    - Complete control library
    """

    # ---------------------------------------------------
    # Fetch Risk
    # ---------------------------------------------------

    risk = get_risk_by_id(
        db,
        risk_id,
    )

    if risk is None:
        raise HTTPException(
            status_code=404,
            detail="Risk not found."
        )

    # ---------------------------------------------------
    # Fetch Existing Controls
    # ---------------------------------------------------

    controls = get_controls_for_risk(
        db,
        risk_id,
    )

    if controls:

        existing_controls = "\n".join(
            [
                f"- {control.title}: {control.description}"
                for control in controls
            ]
        )

    else:

        existing_controls = (
            "No controls have been implemented yet."
        )

    # ---------------------------------------------------
    # Fetch All Available Controls
    # ---------------------------------------------------

    all_controls = get_all_controls(db)

    if all_controls:

        available_controls = "\n".join(
            [
                f"- {control.title}: {control.description}"
                for control in all_controls
            ]
        )

    else:

        available_controls = (
            "No controls exist in the CyberGRC platform."
        )

    # ---------------------------------------------------
    # Build Prompt
    # ---------------------------------------------------

    prompt = CONTROL_RECOMMENDATION_PROMPT.format(
        title=risk.title,
        description=risk.description,
        existing_controls=existing_controls,
        available_controls=available_controls,
    )

    provider = get_ai_provider()

    # ---------------------------------------------------
    # Retry if AI returns invalid JSON
    # ---------------------------------------------------

    for attempt in range(2):

        response = provider.generate(prompt)

        try:

            response_json = json.loads(response)

            # ---------------------------------------------------
            # Match Recommended Existing Controls
            # ---------------------------------------------------

            for recommendation in response_json.get(
                "recommended_existing_controls",
                [],
            ):

                matched_control, confidence = match_control(
                    recommendation["control_name"],
                    all_controls,
                )

                if (
                    matched_control is not None
                    and confidence >= 0.70
                ):

                    recommendation["control_id"] = (
                        matched_control.id
                    )

                    recommendation["already_exists"] = True

                    recommendation["confidence"] = round(
                        confidence,
                        2,
                    )

                else:

                    recommendation["control_id"] = None

                    recommendation["already_exists"] = False

                    recommendation["confidence"] = round(
                        confidence,
                        2,
                    )

            # ---------------------------------------------------
            # Match Recommended New Controls
            # ---------------------------------------------------

            for recommendation in response_json.get(
                "recommended_new_controls",
                [],
            ):

                matched_control, confidence = match_control(
                    recommendation["control_name"],
                    all_controls,
                )

                if (
                    matched_control is not None
                    and confidence >= 0.90
                ):

                    recommendation["control_id"] = (
                        matched_control.id
                    )

                    recommendation["already_exists"] = True

                    recommendation["confidence"] = round(
                        confidence,
                        2,
                    )

                else:

                    recommendation["control_id"] = None

                    recommendation["already_exists"] = False

                    recommendation["confidence"] = round(
                        confidence,
                        2,
                    )

            return ControlRecommendationResponse(
                **response_json
            )

        except (
            json.JSONDecodeError,
            ValidationError,
        ):

            if attempt == 0:

                prompt += """

IMPORTANT

Your previous response was invalid.

Return ONLY valid JSON.

Return ONLY the required schema.

Do not include markdown.

Do not include explanations.

"""

                continue

            raise HTTPException(
                status_code=500,
                detail="AI returned invalid JSON after retry."
            )

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=f"AI recommendation failed: {str(e)}"
            )