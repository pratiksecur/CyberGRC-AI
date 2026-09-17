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
    """

    generated_at: datetime

    risk_id: int

    risk_score: int

    alerts: list[MonitoringAlert]