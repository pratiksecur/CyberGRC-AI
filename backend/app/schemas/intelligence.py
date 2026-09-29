from datetime import date

from pydantic import BaseModel, ConfigDict


# ==========================================================
# EVIDENCE
# ==========================================================


class IntelligenceEvidence(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    control_id: int
    title: str
    file_name: str


# ==========================================================
# FRAMEWORK
# ==========================================================


class IntelligenceFramework(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    name: str
    version: str
    control_code: str


# ==========================================================
# CORRECTIVE ACTION
# ==========================================================


class IntelligenceAction(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    finding_id: int
    title: str
    priority: str
    status: str | None
    assigned_to: int
    due_date: date
    overdue: bool


# ==========================================================
# AUDIT FINDING
# ==========================================================


class IntelligenceFinding(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    audit_id: int
    control_id: int
    title: str
    severity: str
    status: str | None

    actions: list[IntelligenceAction]


# ==========================================================
# CONTROL
# ==========================================================


class IntelligenceControl(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    title: str
    status: str | None
    effectiveness: int

    evidence: list[IntelligenceEvidence]
    frameworks: list[IntelligenceFramework]
    findings: list[IntelligenceFinding]


# ==========================================================
# CONTINUOUS RISK STATE
# ==========================================================


class IntelligenceRiskStateReason(BaseModel):
    """
    Deterministic reason explaining why the continuous
    risk state is CURRENT, DEGRADED, or requires
    reassessment.
    """

    code: str
    severity: str
    message: str

    resource_type: str | None = None
    resource_id: int | None = None


# ==========================================================
# CONTINUOUS RISK RESPONSE
# ==========================================================


class IntelligenceRiskResponseDecision(BaseModel):
    """
    Deterministic Phase 57 response decision.

    This describes what should be considered next. It does
    not mean the action has been executed.
    """

    decision: str
    priority: str
    reason_codes: list[str]
    human_approval_required: bool


class IntelligenceRiskResponse(BaseModel):
    """
    Deterministic response orchestration derived from the
    Phase 56 continuous risk state.
    """

    response_required: bool
    priority: str
    human_approval_required: bool
    decisions: list[
        IntelligenceRiskResponseDecision
    ]


# ==========================================================
# RISK INTELLIGENCE METRICS
# ==========================================================


class RiskIntelligenceMetrics(BaseModel):
    control_count: int

    controls_with_evidence: int
    evidence_coverage_percent: float

    average_control_effectiveness: float

    framework_count: int

    finding_count: int
    open_findings: int
    critical_findings: int

    action_count: int
    open_actions: int
    overdue_actions: int

    remediation_completion_percent: float

    # ------------------------------------------------------
    # Residual risk
    # ------------------------------------------------------

    estimated_residual_risk: float

    control_estimated_residual_risk: float

    # ------------------------------------------------------
    # Risk treatment intelligence
    # ------------------------------------------------------

    treatment_count: int

    effective_treatment_count: int

    treatment_residual_risk: float | None

    treatment_aware_residual_risk: float

    selected_treatment_id: int | None

    # ------------------------------------------------------
    # Phase 56 — Continuous risk state
    # ------------------------------------------------------

    continuous_risk_state: str

    treatment_state: str

    reassessment_required: bool

    state_reasons: list[
        IntelligenceRiskStateReason
    ]

    # ------------------------------------------------------
    # Phase 57 — Continuous risk response
    # ------------------------------------------------------

    response_required: bool

    response_priority: str

    human_approval_required: bool

    response_decisions: list[
        IntelligenceRiskResponseDecision
    ]


# ==========================================================
# RISK INTELLIGENCE RESPONSE
# ==========================================================


class RiskIntelligenceResponse(BaseModel):
    risk_id: int
    risk_title: str
    risk_score: int
    risk_status: str | None
    owner_id: int

    metrics: RiskIntelligenceMetrics

    controls: list[IntelligenceControl]


# ==========================================================
# OVERVIEW METRICS
# ==========================================================


class GRCIntelligenceOverviewMetrics(BaseModel):
    total_risks: int
    critical_risks: int

    risks_with_controls: int
    risks_with_evidence: int

    total_findings: int
    open_findings: int
    critical_findings: int

    total_actions: int
    open_actions: int
    overdue_actions: int

    remediation_completion_percent: float


# ==========================================================
# OVERVIEW RESPONSE
# ==========================================================


class GRCIntelligenceOverviewResponse(BaseModel):
    metrics: GRCIntelligenceOverviewMetrics

    risks: list[RiskIntelligenceResponse]