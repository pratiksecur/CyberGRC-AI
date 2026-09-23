import api from "./axios";


export interface RiskTreatment {
  id: number;

  risk_id: number;

  strategy:
    | "Mitigate"
    | "Avoid"
    | "Transfer"
    | "Accept";

  status:
    | "Planned"
    | "In Progress"
    | "Completed"
    | "Cancelled";

  treatment_plan: string;

  owner_id: number;

  target_date: string | null;

  residual_likelihood: number | null;

  residual_impact: number | null;

  residual_risk_score: number | null;

  acceptance_status:
    | "Not Required"
    | "Pending"
    | "Approved"
    | "Rejected";

  acceptance_reason: string | null;

  accepted_by_id: number | null;

  accepted_at: string | null;

  created_at: string;

  updated_at: string;
}


export interface CreateRiskTreatmentRequest {
  risk_id: number;

  strategy:
    | "Mitigate"
    | "Avoid"
    | "Transfer"
    | "Accept";

  status:
    | "Planned"
    | "In Progress"
    | "Completed"
    | "Cancelled";

  treatment_plan: string;

  owner_id: number;

  target_date: string | null;

  residual_likelihood: number | null;

  residual_impact: number | null;

  residual_risk_score: number | null;

  acceptance_status:
    | "Not Required"
    | "Pending"
    | "Approved"
    | "Rejected";

  acceptance_reason: string | null;
}


export type UpdateRiskTreatmentRequest =
  Partial<
    Omit<
      CreateRiskTreatmentRequest,
      "risk_id"
    >
  >;


export async function getRiskTreatments(): Promise<
  RiskTreatment[]
> {
  const response = await api.get(
    "/risk-treatments/"
  );

  return response.data;
}


export async function getRiskTreatment(
  id: number
): Promise<RiskTreatment> {
  const response = await api.get(
    `/risk-treatments/${id}`
  );

  return response.data;
}


export async function getRiskTreatmentsForRisk(
  riskId: number
): Promise<RiskTreatment[]> {
  const response = await api.get(
    `/risks/${riskId}/treatments`
  );

  return response.data;
}


export async function createRiskTreatment(
  data: CreateRiskTreatmentRequest
): Promise<RiskTreatment> {
  const response = await api.post(
    "/risk-treatments/",
    data
  );

  return response.data;
}


export async function updateRiskTreatment(
  id: number,
  data: UpdateRiskTreatmentRequest
): Promise<RiskTreatment> {
  const response = await api.patch(
    `/risk-treatments/${id}`,
    data
  );

  return response.data;
}


export async function deleteRiskTreatment(
  id: number
): Promise<void> {
  await api.delete(
    `/risk-treatments/${id}`
  );
}