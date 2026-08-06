import api from "./axios";

export interface RiskTrend {
  month: string;
  risks: number;
}

export const getRiskTrend = async (): Promise<RiskTrend[]> => {
  const response = await api.get("/dashboard/risk-trend");
  return response.data;
};