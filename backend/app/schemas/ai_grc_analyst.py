from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AIGRCAnalystRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
    )


class AIGRCAnalystResponse(BaseModel):
    question: str

    category: str

    analysis: str

    recommendations: list[str] = Field(
        default_factory=list
    )

    supporting_signals: dict[str, Any] = Field(
        default_factory=dict
    )

    human_decision_required: bool = True

    generated_at: str