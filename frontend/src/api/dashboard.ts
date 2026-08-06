import api from "./axios";

export interface DashboardResponse {
  totalRisks: number;
  controls: number;
  audits: number;
  compliance: number;
  securityHealth: number;
  criticalRisks: number;
  activeControls: number;
}

export const getDashboard = async (): Promise<DashboardResponse> => {
  const response = await api.get("/dashboard");
  return response.data;
};