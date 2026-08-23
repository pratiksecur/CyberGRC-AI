import { useQuery } from "@tanstack/react-query";

import { getRiskReport } from "@/api/reports";

export function useRiskReport() {
  return useQuery({
    queryKey: ["risk-report"],
    queryFn: getRiskReport,
  });
}