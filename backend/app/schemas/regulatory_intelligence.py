from datetime import datetime

from pydantic import BaseModel


class RegulatoryControlIntelligenceResponse(
    BaseModel
):
    control_id: int
    control_title: str
    control_status: str | None
    effectiveness: int
    control_state: str

    evidence_count: int
    evidence_state: str
    evidence_freshness_score: float

    risk_ids: list[int]
    risk_scores: list[int]
    risk_exposure: str


class RegulatoryRequirementIntelligenceResponse(
    BaseModel
):
    requirement_id: int
    requirement_code: str
    requirement_title: str
    requirement_description: str

    mapped_control_count: int
    control_ids: list[int]

    controls: list[
        RegulatoryControlIntelligenceResponse
    ]

    state: str
    exposure: str


class RegulatoryFrameworkIntelligenceResponse(
    BaseModel
):
    framework_id: int
    framework_name: str
    framework_version: str

    requirement_count: int
    covered_requirements: int
    partial_requirements: int
    gap_requirements: int

    critical_requirements: int
    high_requirements: int

    coverage_percent: float

    requirements: list[
        RegulatoryRequirementIntelligenceResponse
    ]


class RegulatoryIntelligenceResponse(
    BaseModel
):
    generated_at: datetime

    framework_count: int

    total_requirements: int
    covered_requirements: int
    partial_requirements: int
    gap_requirements: int

    critical_requirements: int
    high_requirements: int

    overall_coverage_percent: float
    overall_posture: str

    overlapping_controls: int

    frameworks: list[
        RegulatoryFrameworkIntelligenceResponse
    ]