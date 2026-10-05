import { useQuery } from "@tanstack/react-query";

import {
  getRiskResponseWorkflows,
} from "@/api/risks";


// ==========================================================
// Phase 60 - Governed Response Workflows
// ==========================================================

export function useRiskResponseWorkflows(
  riskId: number
) {
  return useQuery({
    queryKey: [
      "risk-response-workflows",
      riskId,
    ],

    queryFn: () =>
      getRiskResponseWorkflows(riskId),

    enabled: !!riskId,

    refetchInterval: 60_000,
  });
}