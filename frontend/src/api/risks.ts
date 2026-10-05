import api from "./axios";

export interface Risk {
  id: number;
  title: string;
  description: string;
  likelihood: number;
  impact: number;
  risk_score: number;
  status: string;
  owner_id: number;
  created_at: string;
  updated_at: string;
}

export interface CreateRiskRequest {
  title: string;
  description: string;
  likelihood: number;
  impact: number;
  owner_id: number;
}


// ==========================================================
// Phase 57 - Continuous Risk Response
// ==========================================================

export interface RiskResponseDecision {
  decision: string;
  priority: string;
  reason_codes: string[];
  human_approval_required: boolean;
}

export interface RiskResponseReason {
  code: string;
  severity: string;
  message: string;
  resource_type: string | null;
  resource_id: number | null;
}

export interface RiskContinuousResponse {
  risk_id: number;

  risk_state: string;

  treatment_state: string;

  reassessment_required: boolean;

  response_required: boolean;

  priority: string;

  human_approval_required: boolean;

  decisions: RiskResponseDecision[];

  reasons: RiskResponseReason[];
}


// ==========================================================
// Phase 60 - Governed Response Workflows
// ==========================================================

export interface RiskResponseWorkflow {
  id: number;

  execution_id: number;

  decision_id: number;

  risk_id: number;

  workflow_type: string;

  status: string;

  target_type: string;

  target_id: number | null;

  title: string;

  description: string;

  created_by_id: number;

  updated_by_id: number | null;

  resolution_reason: string | null;

  started_at: string | null;

  completed_at: string | null;

  cancelled_at: string | null;

  created_at: string;

  updated_at: string;
}


// ==========================================================
// Phase 61 - Workflow Intelligence
// ==========================================================

export interface RiskResponseWorkflowIntelligence {
  workflow_id: number;

  risk_id: number;

  status: string;

  health: string;

  age_days: number;

  age_seconds: number;

  attention_required: boolean;

  reason_codes: string[];

  started: boolean;

  terminal: boolean;

  time_to_start_seconds: number | null;

  time_in_progress_seconds: number | null;

  lifecycle_duration_seconds: number | null;

  terminal_age_seconds: number | null;

  decision_priority: string | null;

  priority_rank: number | null;

  governance_level: string | null;

  priority_requires_attention: boolean;

  priority_reason_codes: string[];

  bottlenecked: boolean;

  bottleneck_reason_codes: string[];

  escalation_recommendation: string;

  escalation_reason_codes: string[];

  escalation_requires_human_review: boolean;

  dependency_state: string;

  dependency_reason_codes: string[];

  dependency_target_type: string | null;

  dependency_target_id: number | null;
}


// ==========================================================
// API - Risk CRUD
// ==========================================================

export async function getRisks(): Promise<Risk[]> {
  const response = await api.get(
    "/risks/"
  );

  return response.data;
}


export async function createRisk(
  data: CreateRiskRequest
): Promise<Risk> {
  const response = await api.post(
    "/risks/",
    data
  );

  return response.data;
}


export async function getRisk(
  id: number
): Promise<Risk> {
  const response = await api.get(
    `/risks/${id}`
  );

  return response.data;
}


export async function updateRisk(
  id: number,
  data: CreateRiskRequest
): Promise<Risk> {
  const response = await api.patch(
    `/risks/${id}`,
    data
  );

  return response.data;
}


export async function deleteRisk(
  id: number
): Promise<void> {
  await api.delete(
    `/risks/${id}`
  );
}


// ==========================================================
// Phase 57 - Continuous Risk Response API
// ==========================================================

export async function getRiskContinuousResponse(
  riskId: number
): Promise<RiskContinuousResponse> {
  const response = await api.get(
    `/risks/${riskId}/continuous-response`
  );

  return response.data;
}


// ==========================================================
// Phase 60 - Governed Response Workflows API
// ==========================================================

export async function getRiskResponseWorkflows(
  riskId: number
): Promise<RiskResponseWorkflow[]> {
  const response = await api.get(
    `/risks/${riskId}/response-workflows`
  );

  return response.data;
}


// ==========================================================
// Phase 61 - Workflow Intelligence API
// ==========================================================

export async function getRiskResponseWorkflowIntelligence(
  riskId: number,
  workflowId: number
): Promise<RiskResponseWorkflowIntelligence> {
  const response = await api.get(
    `/risks/${riskId}/response-workflows/${workflowId}/intelligence`
  );

  return response.data;
}