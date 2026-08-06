import { useQuery } from "@tanstack/react-query";
import { getRiskTrend } from "@/api/riskTrend";

export function useRiskTrend() {
  return useQuery({
    queryKey: ["risk-trend"],
    queryFn: getRiskTrend,
  });
}