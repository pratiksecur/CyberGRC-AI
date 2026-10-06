from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.ai.governance import (
    secure_prompt,
    validate_raw_response,
)
from app.ai.provider_factory import (
    get_ai_provider,
)

from app.services.ai_grc_analyst_service import (
    build_ai_grc_analyst_context,
    build_analyst_prompt,
    get_analyst_question_category,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _extract_recommendations(
    response: str,
) -> list[str]:
    recommendations: list[str] = []

    lines = response.splitlines()

    for line in lines:
        normalized = line.strip()

        if not normalized:
            continue

        if (
            normalized.startswith("- ")
            or normalized.startswith("* ")
        ):
            recommendations.append(
                normalized[2:].strip()
            )

        elif (
            normalized[:2].isdigit()
            and ". " in normalized[:4]
        ):
            recommendations.append(
                normalized.split(
                    ". ",
                    1,
                )[1].strip()
            )

    return recommendations[:8]


def analyze_with_ai(
    db: Session,
    question: str,
    visible_user_ids: list[int],
) -> dict[str, Any]:
    context = build_ai_grc_analyst_context(
        db,
        visible_user_ids,
    )

    prompt = build_analyst_prompt(
        question,
        context,
    )

    secured_prompt = secure_prompt(
        prompt
    )

    provider = get_ai_provider()

    raw_response = provider.generate(
        secured_prompt
    )

    validated_response = validate_raw_response(
        raw_response
    )

    analysis = validated_response.strip()

    return {
        "question": question,
        "category": get_analyst_question_category(
            question
        ),
        "analysis": analysis,
        "recommendations": _extract_recommendations(
            analysis
        ),
        "supporting_signals": {
            "risk_summary":
                context["risk_summary"],
            "control_summary":
                context["control_summary"],
            "evidence_summary":
                context["evidence_summary"],
            "finding_summary":
                context["finding_summary"],
            "corrective_action_summary":
                context[
                    "corrective_action_summary"
                ],
            "regulatory_summary":
                context["regulatory_summary"],
            "control_intelligence_summary":
                context[
                    "control_intelligence_summary"
                ],
        },
        "human_decision_required": True,
        "generated_at":
            _utcnow().isoformat(),
    }