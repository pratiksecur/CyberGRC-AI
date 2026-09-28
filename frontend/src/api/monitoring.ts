import api from "./axios";


// ==========================================================
// MONITORING ALERT
// ==========================================================

export interface MonitoringAlert {
  alert_type: string;

  severity: string;

  resource_type: string;

  resource_id: number;

  title: string;

  message: string;

  risk_id: number | null;

  detected_at: string;
}


// ==========================================================
// RISK STATE REASON
// ==========================================================

export interface RiskStateReason {
  code: string;

  severity: string;

  message: string;

  resource_type: string | null;

  resource_id: number | null;
}


// ==========================================================
// MONITORING METRICS
// ==========================================================

export interface MonitoringMetrics {
  total_alerts: number;

  critical_alerts: number;

  high_alerts: number;

  medium_alerts: number;

  low_alerts: number;

  critical_risks: number;

  risks_without_controls: number;

  controls_without_evidence: number;

  ineffective_controls: number;

  critical_findings: number;

  open_findings: number;

  overdue_actions: number;

  critical_actions: number;

  stale_evidence: number;

  // --------------------------------------------------------
  // Risk Treatment Monitoring
  // --------------------------------------------------------

  treatment_alerts: number;

  overdue_treatments: number;

  stuck_treatments: number;

  planned_high_risk_treatments: number;

  pending_acceptances: number;

  elevated_residual_risks: number;

  cancelled_without_replacement: number;

  approved_acceptances: number;

  // --------------------------------------------------------
  // Phase 56 - Continuous Risk State
  // --------------------------------------------------------

  degraded_risks: number;

  reassessment_required_risks: number;
}


// ==========================================================
// MONITORING OVERVIEW
// ==========================================================

export interface MonitoringOverviewResponse {
  generated_at: string;

  metrics: MonitoringMetrics;

  alerts: MonitoringAlert[];
}


// ==========================================================
// RISK MONITORING
// ==========================================================

export interface RiskMonitoringResponse {
  generated_at: string;

  risk_id: number;

  risk_score: number;

  alerts: MonitoringAlert[];

  // --------------------------------------------------------
  // Phase 56 - Continuous Risk State
  // --------------------------------------------------------

  continuous_risk_state: string;

  treatment_state: string;

  reassessment_required: boolean;

  state_reasons: RiskStateReason[];
}


// ==========================================================
// API
// ==========================================================

export async function getMonitoringOverview(): Promise<MonitoringOverviewResponse> {
  const response = await api.get(
    "/monitoring/overview"
  );

  return response.data;
}


export async function getRiskMonitoring(
  riskId: number
): Promise<RiskMonitoringResponse> {
  const response = await api.get(
    `/monitoring/risk/${riskId}`
  );

  return response.data;
}