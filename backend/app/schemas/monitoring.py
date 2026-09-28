from datetime import datetime


from pydantic import BaseModel


# ==========================================================
# MONITORING ALERT
# ==========================================================

class MonitoringAlert(BaseModel):
    """
    One deterministic GRC monitoring alert.

    Alerts are derived from the current database state.
    They are intentionally not persisted as a separate model
    in Phase 46.
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