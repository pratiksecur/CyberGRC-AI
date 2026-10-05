from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ==========================================================
# Existing Evidence Schemas
# ==========================================================


class EvidenceCreate(BaseModel):
    control_id: int

    title: str

    description: str

    file_name: str

    file_path: str


class EvidenceUpdate(BaseModel):
    title: Optional[str] = None

    description: Optional[str] = None

    file_name: Optional[str] = None

    file_path: Optional[str] = None


class EvidenceResponse(BaseModel):
    id: int

    control_id: int

    title: str

    description: str

    file_name: str

    file_path: str

    uploaded_by: int

    uploaded_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ==========================================================
# Phase 62 - Evidence Intelligence
# ==========================================================


class EvidenceIntelligenceItemResponse(BaseModel):
    evidence_id: int
    control_id: int
    risk_ids: list[int]

    age_days: float | None

    freshness: str
    freshness_score: int

    completeness: str
    completeness_score: int

    quality: str
    quality_score: int

    quality_indicators: list[str]

    evidence_to_control_mapped: bool
    evidence_to_risk_mapped: bool

    file_available: bool


class MissingEvidenceResponse(BaseModel):
    control_id: int
    control_title: str
    priority: str
    reason: str
    recommended_action: str


class EvidenceCollectionWorkflowResponse(BaseModel):
    control_id: int
    control_title: str
    priority: str
    workflow_type: str
    status: str
    recommended_action: str


class EvidenceCoverageResponse(BaseModel):
    total_controls: int
    controls_with_evidence: int
    controls_without_evidence: int
    coverage_percent: float

    total_evidence: int
    fresh_evidence: int
    aging_evidence: int
    stale_evidence: int

    risk_mapped_evidence: int

    average_quality_score: float
    average_completeness_score: float

    audit_readiness_score: float
    audit_ready: bool


class EvidenceIntelligenceResponse(BaseModel):
    coverage: EvidenceCoverageResponse

    evidence: list[
        EvidenceIntelligenceItemResponse
    ]

    missing_evidence: list[
        MissingEvidenceResponse
    ]

    collection_workflows: list[
        EvidenceCollectionWorkflowResponse
    ]

    audit_package_evidence_ids: list[int]