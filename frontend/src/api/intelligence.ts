import api from "./axios";


// ==========================================================
// INTELLIGENCE EVIDENCE
// ==========================================================

export interface IntelligenceEvidence {
  id: number;
  control_id: number;
  title: string;
  file_name: string;
}


// ==========================================================
// INTELLIGENCE FRAMEWORK
// ==========================================================

export interface IntelligenceFramework {
  id: number;
  name: string;
  version: string;
  control_code: string;
}


// ==========================================================
// INTELLIGENCE ACTION
// ==========================================================

export interface IntelligenceAction {
  id: number;
  finding_id: number;
  title: string;
  priority: string;
  status: string | null;
  assigned_to: number;
  due_date: string;
  overdue: boolean;
}


// ==========================================================
// INTELLIGENCE FINDING
// ==========================================================

export interface IntelligenceFinding {
  id: number;
  audit_id: number;
  control_id: number;
  title: string;
  severity: string;
  status: string | null;
  actions: IntelligenceAction[];
}


// ==========================================================
// INTELLIGENCE CONTROL
// ==========================================================

export interface IntelligenceControl {
  id: number;
  title: string;
  status: string | null;
  effectiveness: number;
  evidence: IntelligenceEvidence[];
  frameworks: IntelligenceFramework[];
  findings: IntelligenceFinding[];
}


// ==========================================================
// RISK INTELLIGENCE METRICS
// ==========================================================

export interface RiskIntelligenceMetrics {
  control_count: number;

  controls_with_evidence: number;
  evidence_coverage_percent: number;

  average_control_effectiveness: number;

  framework_count: number;

  finding_count: number;
  open_findings: number;
  critical_findings: number;

  action_count: number;
  open_actions: number;
  overdue_actions: number;

  remediation_completion_percent: number;

  estimated_residual_risk: number;
}


// ==========================================================
// RISK INTELLIGENCE RESPONSE
// ==========================================================

export interface RiskIntelligenceResponse {
  risk_id: number;
  risk_title: string;
  risk_score: number;
  risk_status: string | null;
  owner_id: number;

  metrics: RiskIntelligenceMetrics;

  controls: IntelligenceControl[];
}


// ==========================================================
// OVERVIEW METRICS
// ==========================================================

export interface GRCIntelligenceOverviewMetrics {
  total_risks: number;
  critical_risks: number;

  risks_with_controls: number;
  risks_with_evidence: number;

  total_findings: number;
  open_findings: number;
  critical_findings: number;

  total_actions: number;
  open_actions: number;
  overdue_actions: number;

  remediation_completion_percent: number;
}


// ==========================================================
// OVERVIEW RESPONSE
// ==========================================================

export interface GRCIntelligenceOverviewResponse {
  metrics: GRCIntelligenceOverviewMetrics;
  risks: RiskIntelligenceResponse[];
}


// ==========================================================
// API
// ==========================================================

export async function getGRCIntelligenceOverview(): Promise<GRCIntelligenceOverviewResponse> {
  const response = await api.get(
    "/intelligence/overview"
  );

  return response.data;
}


export async function getRiskIntelligence(
  riskId: number
): Promise<RiskIntelligenceResponse> {
  const response = await api.get(
    `/intelligence/risk/${riskId}`
  );

  return response.data;
}