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
from app.ai.prompts import CONTROL_RECOMMENDATION_PROMPT

from app.auth.ai_access import (
    get_authorized_controls,
    get_authorized_risk,
)

from app.models.user import User

from app.schemas.ai import (
    ControlRecommendationResponse,
)

from app.services.risk_control_service import (
    get_controls_for_risk,
)

from app.services.ai.control_matcher import (
    match_control,
)


def recommend_controls(
    db: Session,
    risk_id: int,
    current_user: User,
) -> ControlRecommendationResponse:
    """
    Generate control recommendations using only the risk and
    control records visible to the authenticated user.
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

    visible_controls = get_authorized_controls(
        db,
        current_user,
    )

    visible_control_ids = {
        control.id
        for control in visible_controls
    }

    existing_controls = [
        control
        for control in get_controls_for_risk(
            db,
            risk_id,
        )
        if control.id in visible_control_ids
    ]

    if existing_controls:
        existing_controls_text = "\n".join(
            f"- {control.title}: {control.description}"
            for control in existing_controls
        )
    else:
        existing_controls_text = (
            "No authorized controls have "
            "been implemented yet."
        )

    if visible_controls:
        available_controls_text = "\n".join(
            f"- {control.title}: {control.description}"
            for control in visible_controls
        )
    else:
        available_controls_text = (
            "No authorized controls exist "
            "in the CyberGRC platform."
        )

    prompt = CONTROL_RECOMMENDATION_PROMPT.format(
        title=risk.title,
        description=risk.description,
        existing_controls=existing_controls_text,
        available_controls=available_controls_text,
    )

    try:
        prompt = secure_prompt(prompt)

    except AIGovernanceError:
        raise HTTPException(
            status_code=503,
            detail="AI request could not be processed.",
        )

    try:
        provider = get_ai_provider()

    except Exception:
        record_ai_event(
            "control_recommendations",
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

    for attempt in range(2):

        try:
            response = validate_raw_response(
                provider.generate(prompt)
            )

            response_json = json.loads(
                response.strip()
            )

            if not isinstance(response_json, dict):
                raise AIGovernanceError(
                    "AI output must be a JSON object."
                )

            for recommendation in response_json.get(
                "recommended_existing_controls",
                [],
            ):

                control_name = recommendation.get(
                    "control_name",
                    "",
                )

                matched_control, confidence = match_control(
                    control_name,
                    visible_controls,
                )

                if (
                    matched_control is not None
                    and confidence >= 0.70
                ):
                    recommendation["control_id"] = (
                        matched_control.id
                    )
                    recommendation["already_exists"] = True
                else:
                    recommendation["control_id"] = None
                    recommendation["already_exists"] = False

                recommendation["confidence"] = round(
                    confidence,
                    2,
                )

            for recommendation in response_json.get(
                "recommended_new_controls",
                [],
            ):

                control_name = recommendation.get(
                    "control_name",
                    "",
                )

                matched_control, confidence = match_control(
                    control_name,
                    visible_controls,
                )

                if (
                    matched_control is not None
                    and confidence >= 0.90
                ):
                    recommendation["control_id"] = (
                        matched_control.id
                    )
                    recommendation["already_exists"] = True
                else:
                    recommendation["control_id"] = None
                    recommendation["already_exists"] = False

                recommendation["confidence"] = round(
                    confidence,
                    2,
                )

            result = validate_ai_model(
                response_json,
                ControlRecommendationResponse,
            )

            record_ai_event(
                "control_recommendations",
                model=model_name,
                outcome="success",
                validation="schema",
            )

            return result

        except AIGovernanceError:

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

            record_ai_event(
                "control_recommendations",
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

IMPORTANT

Your previous response was invalid.

Return ONLY valid JSON.

Return ONLY the required schema.

Do not include markdown.

Do not include explanations.
"""
                continue

            record_ai_event(
                "control_recommendations",
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
                "control_recommendations",
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