from datetime import datetime

from pydantic import BaseModel, Field


class ControlIntelligenceItemResponse(BaseModel):
    control_id: int
    title: str
    control_type: str
    status: str

    effectiveness: int = Field(
        ge=0,
        le=100,
    )

    health_score: float
    health_state: str
    effectiveness_trend_signal: str

    evidence_count: int
    fresh_evidence: int
    aging_evidence: int
    stale_evidence: int
    evidence_freshness_score: float
    evidence_state: str

    risk_count: int
    high_risk_count: int
    critical_risk_count: int

    risk_ids: list[int]
    risk_titles: list[str]

    framework_count: int
    framework_names: list[str]

    open_finding_count: int
    critical_finding_count: int

    open_corrective_action_count: int
    overdue_corrective_action_count: int

    monitoring_signals: list[str]

    remediation_required: bool

    recommended_action: str


class ControlIntelligenceSummaryResponse(BaseModel):
    total_controls: int
    active_controls: int

    healthy_controls: int
    degraded_controls: int
    critical_controls: int

    ineffective_controls: int
    controls_without_evidence: int
    stale_evidence: int

    framework_mapped_controls: int
    risk_mapped_controls: int

    evidence_coverage_percent: float
    framework_coverage_percent: float
    risk_coverage_percent: float

    average_effectiveness: float
    average_health_score: float

    open_exceptions: int
    critical_exceptions: int

    remediation_required: int

    overall_posture: str


class ControlIntelligenceResponse(BaseModel):
    generated_at: datetime

    summary: ControlIntelligenceSummaryResponse

    controls: list[
        ControlIntelligenceItemResponse
    ]