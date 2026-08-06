import api from "./axios";

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