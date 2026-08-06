import api from "./axios";

export interface AISummaryResponse {
  organizationRiskLevel: string;
  executiveSummary: string;
  topPriorities: string[];
  recommendedNextSteps: string[];
}

export const getAISummary = async (): Promise<AISummaryResponse> => {
  const response = await api.post("/ai/dashboard-summary");
  return response.data;
};