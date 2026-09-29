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
// API - Risk CRUD
// ==========================================================

export async function getRisks(): Promise<Risk[]> {
  const response = await api.get("/risks/");

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