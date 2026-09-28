import api from "./axios";

// ==========================================================
// Executive Summary
// ==========================================================

export interface ExecutiveSummary {
  organization_risk_level: string;
  executive_summary: string;
  top_priorities: string[];
  recommended_next_steps: string[];
}

export async function getExecutiveSummary(): Promise<ExecutiveSummary> {
  const response = await api.get(
    "/ai/dashboard/executive-summary"
  );

  return response.data;
}

// ==========================================================
// Risk Analysis
// ==========================================================

export interface RiskAnalysis {
  likelihood: string;
  impact: string;
  risk_score: number;
  summary: string;
  recommended_controls: string[];
}

export async function analyzeRisk(
  riskId: number
): Promise<RiskAnalysis> {
  const response = await api.post(
    `/ai/risk/${riskId}/analyze`
  );

  return response.data;
}

// ==========================================================
// Control Recommendation
// ==========================================================

export interface AIControlRecommendation {
  control_id: number | null;
  control_name: string;
  already_exists: boolean;
  confidence: number;
  priority: string;
  reason: string;
}

export interface ControlRecommendation {
  overall_assessment: string;
  existing_controls_assessment: string;

  recommended_existing_controls:
    AIControlRecommendation[];

  recommended_new_controls:
    AIControlRecommendation[];
}

export async function recommendControls(
  riskId: number
): Promise<ControlRecommendation> {
  const response = await api.post(
    `/ai/risk/${riskId}/recommend-controls`
  );

  return response.data;
}

// ==========================================================
// Audit Summary
// ==========================================================

export interface AuditSummary {
  overall_assessment: string;

  critical_findings: number;

  open_findings: number;

  completed_actions: number;

  pending_actions: number;

  executive_summary: string;

  priority_recommendations: string[];
}

export async function summarizeAudit(
  auditId: number
): Promise<AuditSummary> {
  const response = await api.post(
    `/ai/audit/${auditId}/summarize`
  );

  return response.data;
}

// ==========================================================
// Continuous Risk State Explanation — Phase 56
// ==========================================================

export interface RiskStateExplanation {
  risk_state:
    | "CURRENT"
    | "DEGRADED"
    | "REASSESSMENT_REQUIRED";

  treatment_state:
    | "CURRENT"
    | "STALE"
    | "DEGRADED"
    | "REQUIRES_REASSESSMENT";

  reassessment_required: boolean;

  explanation: string;

  key_drivers: string[];

  review_areas: string[];
}

export async function explainRiskState(
  riskId: number
): Promise<RiskStateExplanation> {
  const response = await api.post(
    `/ai/risk/${riskId}/state-explanation`
  );

  return response.data;
}