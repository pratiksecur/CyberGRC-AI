from datetime import datetime
from typing import Literal

from pydantic import BaseModel

CrosswalkConfidence = Literal["direct", "broad"]


class CrosswalkTheme(BaseModel):
    key: str
    label: str


class CrosswalkRequirement(BaseModel):
    """A framework requirement as it appears in crosswalk results."""

    framework_control_id: int
    control_code: str
    title: str
    framework_id: int
    framework_name: str


class CrosswalkRelatedRequirement(CrosswalkRequirement):
    shared_themes: list[CrosswalkTheme]
    confidence: CrosswalkConfidence
    mapped_control_count: int


class CrosswalkRelatedResponse(BaseModel):
    requirement: CrosswalkRequirement
    themes: list[CrosswalkTheme]
    in_crosswalk: bool
    is_umbrella: bool
    related: list[CrosswalkRelatedRequirement]


class CrosswalkSuggestion(CrosswalkRequirement):
    """A requirement a control may also support, for human review."""

    shared_themes: list[CrosswalkTheme]
    confidence: CrosswalkConfidence
    because_of: list[CrosswalkRequirement]


class CrosswalkSuggestionsResponse(BaseModel):
    control_id: int
    mapped_requirement_count: int
    suggestions: list[CrosswalkSuggestion]


class CrosswalkCandidateControl(BaseModel):
    control_id: int
    control_title: str
    confidence: CrosswalkConfidence
    shared_themes: list[CrosswalkTheme]
    via: list[CrosswalkRequirement]


class CrosswalkOpportunity(CrosswalkRequirement):
    """An unmapped requirement that existing controls may already support."""

    best_confidence: CrosswalkConfidence
    candidates: list[CrosswalkCandidateControl]


class CrosswalkFrameworkSummary(BaseModel):
    framework_id: int
    framework_name: str
    requirement_count: int
    unmapped_requirements: int
    opportunities: int


class CrosswalkOpportunitiesResponse(BaseModel):
    generated_at: datetime

    total_requirements: int
    unmapped_requirements: int
    opportunity_count: int
    direct_opportunity_count: int

    frameworks: list[CrosswalkFrameworkSummary]
    opportunities: list[CrosswalkOpportunity]

    disclaimer: str
