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

export async function getRisks(): Promise<Risk[]> {
  const response = await api.get("/risks/");
  return response.data;
}

export async function createRisk(
  data: CreateRiskRequest
): Promise<Risk> {
  const response = await api.post("/risks/", data);
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