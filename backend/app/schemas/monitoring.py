from datetime import datetime

from pydantic import BaseModel, Field


# ==========================================================
# MONITORING ALERT
# ==========================================================

class MonitoringAlert(BaseModel):
    """
    One deterministic GRC monitoring alert.

    Alerts are derived from the current database state.
    They are intentionally not persisted as a separate model.
    """

    alert_type: str

    severity: str

    resource_type: str

    resource_id: int

    title: str

    message: str

    risk_id: int | None = None

    detected_at: datetime


# ==========================================================
# PHASE 57 — MONITORING RISK RESPONSE DECISION
# ==========================================================

class MonitoringRiskResponseDecision(BaseModel):
    """
    One deterministic response decision associated with a risk.

    Response decisions are advisory and do not execute
    automatically.
    """

    decision: str

    priority: str

    reason_codes: list[str]

    human_approval_required: bool


# ==========================================================
# PHASE 57 — MONITORING RISK RESPONSE
# ==========================================================

# ==========================================================
# PHASE 57 — MONITORING RISK RESPONSE
# ==========================================================

class MonitoringRiskResponse(BaseModel):
    """
    Deterministic Phase 57 response posture for one visible risk.
    """

    risk_id: int

    risk_state: str

    treatment_state: str

    reassessment_required: bool

    response_required: bool

    priority: str

    human_approval_required: bool

    decisions: list[MonitoringRiskResponseDecision]


# ==========================================================
# MONITORING METRICS
# ==========================================================

class MonitoringMetrics(BaseModel):
    """
    Aggregated monitoring state visible to the current user.
    """

    total_alerts: int

    critical_alerts: int

    high_alerts: int

    medium_alerts: int

    low_alerts: int

    critical_risks: int

    risks_without_controls: int

    controls_without_evidence: int

    ineffective_controls: int

    critical_findings: int

    open_findings: int

    overdue_actions: int

    critical_actions: int

    stale_evidence: int

    # ------------------------------------------------------
    # Risk-treatment intelligence signals
    # ------------------------------------------------------

    treatment_alerts: int = 0

    overdue_treatments: int = 0

    stuck_treatments: int = 0

    planned_high_risk_treatments: int = 0

    pending_acceptances: int = 0

    elevated_residual_risks: int = 0

    cancelled_without_replacement: int = 0

    approved_acceptances: int = 0

    # ------------------------------------------------------
    # Phase 56 — Continuous Risk State
    # ------------------------------------------------------

    degraded_risks: int = 0

    reassessment_required_risks: int = 0

    # ------------------------------------------------------
    # Phase 57 — Continuous Risk Response
    # ------------------------------------------------------

    response_required_risks: int = 0

    human_approval_required_risks: int = 0

    critical_response_risks: int = 0


# ==========================================================
# MONITORING OVERVIEW
# ==========================================================

class MonitoringOverviewResponse(BaseModel):
    """
    Scope-aware monitoring overview.
    """

    generated_at: datetime

    metrics: MonitoringMetrics

    alerts: list[MonitoringAlert]

    # ------------------------------------------------------
    # Phase 57 — Continuous Risk Response
    # ------------------------------------------------------

    risk_responses: list[MonitoringRiskResponse] = Field(
        default_factory=list
    )


# ==========================================================
# RISK MONITORING RESPONSE
# ==========================================================

class RiskMonitoringResponse(BaseModel):
    """
    Monitoring information for one risk.

    Phase 56 adds deterministic continuous-risk-state information.
    """

    generated_at: datetime

    risk_id: int

    risk_score: int

    alerts: list[MonitoringAlert]

    # ------------------------------------------------------
    # Phase 56 — Continuous Risk State
    # ------------------------------------------------------

    continuous_risk_state: str

    treatment_state: str

    reassessment_required: bool

    state_reasons: list[dict]