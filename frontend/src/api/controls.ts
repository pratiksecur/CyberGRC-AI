import api from "./axios";

export interface Control {
  id: number;
  title: string;
  description: string;
  control_type: string;
  status: string;
  effectiveness: number;
  owner_id: number;
  created_at: string;
  updated_at: string;
}

export interface CreateControlRequest {
  title: string;
  description: string;
  control_type: string;
  status: string;
  effectiveness: number;
  owner_id: number;
}

export async function getControls(): Promise<Control[]> {
  const response = await api.get("/controls/");
  return response.data;
}

export async function getControl(
  id: number
): Promise<Control> {
  const response = await api.get(
    `/controls/${id}`
  );

  return response.data;
}

export async function createControl(
  data: CreateControlRequest
): Promise<Control> {
  const response = await api.post(
    "/controls/",
    data
  );

  return response.data;
}

export async function updateControl(
  id: number,
  data: CreateControlRequest
): Promise<Control> {
  const response = await api.patch(
    `/controls/${id}`,
    data
  );

  return response.data;
}

export async function deleteControl(
  id: number
) {
  await api.delete(
    `/controls/${id}`
  );
}

export interface ControlIntelligence {
  control_id: number;
  title: string;
  control_type: string;
  status: string;

  effectiveness: number;

  health_score: number;
  health_state: string;
  effectiveness_trend_signal: string;

  evidence_count: number;
  fresh_evidence: number;
  aging_evidence: number;
  stale_evidence: number;
  evidence_freshness_score: number;
  evidence_state: string;

  risk_count: number;
  high_risk_count: number;
  critical_risk_count: number;

  risk_ids: number[];
  risk_titles: string[];

  framework_count: number;
  framework_names: string[];

  open_finding_count: number;
  critical_finding_count: number;

  open_corrective_action_count: number;
  overdue_corrective_action_count: number;

  monitoring_signals: string[];

  remediation_required: boolean;

  recommended_action: string;
}

export interface ControlIntelligenceSummary {
  total_controls: number;
  active_controls: number;

  healthy_controls: number;
  degraded_controls: number;
  critical_controls: number;

  ineffective_controls: number;
  controls_without_evidence: number;
  stale_evidence: number;

  framework_mapped_controls: number;
  risk_mapped_controls: number;

  evidence_coverage_percent: number;
  framework_coverage_percent: number;
  risk_coverage_percent: number;

  average_effectiveness: number;
  average_health_score: number;

  open_exceptions: number;
  critical_exceptions: number;

  remediation_required: number;

  overall_posture: string;
}

export interface ControlIntelligenceResponse {
  generated_at: string;

  summary: ControlIntelligenceSummary;

  controls: ControlIntelligence[];
}

export async function getControlIntelligence(): Promise<
  ControlIntelligenceResponse
> {
  const response = await api.get(
    "/controls/intelligence"
  );

  return response.data;
}