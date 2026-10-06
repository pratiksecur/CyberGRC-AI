from datetime import date, datetime

from pydantic import BaseModel, Field


class AuditAssuranceAuditResponse(BaseModel):
    id: int
    name: str
    status: str

    start_date: date
    end_date: date

    overdue: bool
    planning_complete: bool

    finding_count: int
    open_findings: int
    critical_findings: int

    control_count: int
    controls_with_evidence: int
    controls_without_evidence: int

    corrective_action_count: int
    open_corrective_actions: int
    overdue_corrective_actions: int
    completed_corrective_actions: int

    closure_ready: bool
    closure_blockers: list[str] = Field(
        default_factory=list
    )


class AuditAssurancePortfolioResponse(BaseModel):
    total_audits: int
    planned: int
    in_progress: int
    completed: int
    overdue: int

    closure_ready: int
    blocked: int


class AuditAssurancePlanningResponse(BaseModel):
    complete: int
    incomplete: int
    completion_percent: float


class AuditAssuranceTestingResponse(BaseModel):
    audits_with_findings: int

    total_findings: int
    open_findings: int
    critical_findings: int

    controls_referenced: int


class AuditAssuranceEvidenceResponse(BaseModel):
    controls_referenced: int
    controls_with_evidence: int
    controls_without_evidence: int

    coverage_percent: float


class AuditAssuranceRemediationResponse(BaseModel):
    total_actions: int

    open_actions: int
    completed_actions: int
    overdue_actions: int


class AuditAssuranceClosureResponse(BaseModel):
    ready: int
    not_ready: int
    blocked: int


class AuditAssuranceSignalResponse(BaseModel):
    signal: str
    severity: str
    count: int
    why: str


class AuditAssuranceScopeResponse(BaseModel):
    visible_audit_users: int
    visible_finding_users: int
    visible_action_users: int
    visible_evidence_users: int

    audit_count: int


class AuditAssuranceResponse(BaseModel):
    generated_at: datetime

    portfolio: AuditAssurancePortfolioResponse

    planning: AuditAssurancePlanningResponse

    testing: AuditAssuranceTestingResponse

    evidence: AuditAssuranceEvidenceResponse

    remediation: AuditAssuranceRemediationResponse

    closure: AuditAssuranceClosureResponse

    assurance_signals: list[
        AuditAssuranceSignalResponse
    ]

    audits: list[
        AuditAssuranceAuditResponse
    ]

    scope: AuditAssuranceScopeResponse