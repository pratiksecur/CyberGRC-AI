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