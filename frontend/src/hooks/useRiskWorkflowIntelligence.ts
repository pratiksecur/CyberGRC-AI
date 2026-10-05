import { useQuery } from "@tanstack/react-query";

import {
  getRiskResponseWorkflowIntelligence,
} from "@/api/risks";


// ==========================================================
// Phase 61 - Workflow Intelligence
// ==========================================================

export function useRiskWorkflowIntelligence(
  riskId: number,
  workflowId: number
) {
  return useQuery({
    queryKey: [
      "risk-response-workflow-intelligence",
      riskId,
      workflowId,
    ],

    queryFn: () =>
      getRiskResponseWorkflowIntelligence(
        riskId,
        workflowId
      ),

    enabled:
      !!riskId &&
      !!workflowId,

    refetchInterval: 60_000,
  });
}