import api from "./axios";

export interface Framework {
  id: number;
  name: string;
  version: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface CreateFrameworkRequest {
  name: string;
  version: string;
  description: string;
}

export async function getFrameworks(): Promise<Framework[]> {
  const response = await api.get("/frameworks/");
  return response.data;
}

export async function getFramework(
  id: number
): Promise<Framework> {
  const response = await api.get(
    `/frameworks/${id}`
  );

  return response.data;
}

export async function createFramework(
  data: CreateFrameworkRequest
): Promise<Framework> {
  const response = await api.post(
    "/frameworks/",
    data
  );

  return response.data;
}

export async function updateFramework(
  id: number,
  data: CreateFrameworkRequest
): Promise<Framework> {
  const response = await api.patch(
    `/frameworks/${id}`,
    data
  );

  return response.data;
}

export async function deleteFramework(
  id: number
) {
  await api.delete(
    `/frameworks/${id}`
  );
}

export interface RegulatoryControlIntelligence {
  control_id: number;
  control_title: string;
  control_status: string | null;
  effectiveness: number;
  control_state: string;

  evidence_count: number;
  evidence_state: string;
  evidence_freshness_score: number;

  risk_ids: number[];
  risk_scores: number[];
  risk_exposure: string;
}

export interface RegulatoryRequirementIntelligence {
  requirement_id: number;
  requirement_code: string;
  requirement_title: string;
  requirement_description: string;

  mapped_control_count: number;
  control_ids: number[];

  controls: RegulatoryControlIntelligence[];

  state: string;
  exposure: string;
}

export interface RegulatoryFrameworkIntelligence {
  framework_id: number;
  framework_name: string;
  framework_version: string;

  requirement_count: number;
  covered_requirements: number;
  partial_requirements: number;
  gap_requirements: number;

  critical_requirements: number;
  high_requirements: number;

  coverage_percent: number;

  requirements: RegulatoryRequirementIntelligence[];
}

export interface RegulatoryIntelligence {
  generated_at: string;

  framework_count: number;

  total_requirements: number;
  covered_requirements: number;
  partial_requirements: number;
  gap_requirements: number;

  critical_requirements: number;
  high_requirements: number;

  overall_coverage_percent: number;
  overall_posture: string;

  overlapping_controls: number;

  frameworks: RegulatoryFrameworkIntelligence[];
}

export async function getRegulatoryIntelligence(): Promise<RegulatoryIntelligence> {
  const response = await api.get(
    "/frameworks/intelligence"
  );

  return response.data;
}