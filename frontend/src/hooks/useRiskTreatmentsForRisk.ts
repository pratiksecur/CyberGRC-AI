import { useQuery } from "@tanstack/react-query";

import {
  getRiskTreatmentsForRisk,
} from "@/api/riskTreatments";


export function useRiskTreatmentsForRisk(
  riskId: number
) {
  return useQuery({
    queryKey: [
      "risk-treatments",
      "risk",
      riskId,
    ],

    queryFn: () =>
      getRiskTreatmentsForRisk(riskId),

    enabled: !!riskId,
  });
}