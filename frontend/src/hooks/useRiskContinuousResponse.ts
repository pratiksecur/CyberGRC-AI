import { useQuery } from "@tanstack/react-query";

import {
  getRiskContinuousResponse,
} from "@/api/risks";


// ==========================================================
// Phase 57 - Continuous Risk Response
// ==========================================================

export function useRiskContinuousResponse(
  riskId: number
) {
  return useQuery({
    queryKey: [
      "risk-continuous-response",
      riskId,
    ],

    queryFn: () =>
      getRiskContinuousResponse(riskId),

    enabled: !!riskId,

    refetchInterval: 60_000,
  });
}