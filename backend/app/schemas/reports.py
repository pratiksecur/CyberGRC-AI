from typing import List

from pydantic import BaseModel


class RiskReportSummary(BaseModel):
    total_risks: int

    critical_risks: int
    high_risks: int
    medium_risks: int
    low_risks: int

    open_risks: int
    closed_risks: int

    average_risk_score: float

    average_treatment_aware_residual_risk: float = 0.0
    total_treatments: int = 0
    risks_with_effective_treatment: int = 0
    pending_acceptances: int = 0
    approved_acceptances: int = 0


class RiskReportItem(BaseModel):
    id: int

    title: str
    description: str

    likelihood: int
    impact: int
    risk_score: int

    treatment_count: int = 0
    effective_treatment_count: int = 0
    treatment_residual_risk: int | None = None
    treatment_aware_residual_risk: float = 0.0
    control_estimated_residual_risk: float = 0.0
    selected_treatment_id: int | None = None
    selected_treatment_strategy: str | None = None
    selected_treatment_status: str | None = None
    selected_treatment_acceptance_status: str | None = None

    status: str

    owner_id: int
    owner_name: str

    created_at: str


class RiskReportResponse(BaseModel):
    summary: RiskReportSummary

    risks: List[RiskReportItem]

class AuditReportSummary(BaseModel):
    total_audits: int

    planned_audits: int
    in_progress_audits: int
    completed_audits: int

    total_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int

    open_findings: int
    closed_findings: int


class AuditReportItem(BaseModel):
    id: int

    name: str
    framework_id: int
    framework_name: str

    auditor_id: int
    auditor_name: str

    scope: str
    status: str

    start_date: str
    end_date: str

    finding_count: int
    critical_finding_count: int
    open_finding_count: int

    created_at: str


class AuditReportResponse(BaseModel):
    summary: AuditReportSummary

    audits: List[AuditReportItem]

class ComplianceReportSummary(BaseModel):
    total_frameworks: int

    total_controls: int
    active_controls: int

    average_control_effectiveness: float

    total_evidence: int

    total_findings: int
    open_findings: int
    critical_findings: int


class FrameworkComplianceItem(BaseModel):
    id: int

    name: str
    version: str

    control_count: int
    active_control_count: int

    average_effectiveness: float

    evidence_count: int

    finding_count: int
    critical_finding_count: int
    open_finding_count: int


class ComplianceReportResponse(BaseModel):
    summary: ComplianceReportSummary

    frameworks: List[FrameworkComplianceItem]