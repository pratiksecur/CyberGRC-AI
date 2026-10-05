import { useMutation } from "@tanstack/react-query";

import {
  explainRiskResponseWorkflow,
  type WorkflowIntelligenceExplanation,
} from "@/api/ai";


export function useRiskWorkflowExplanation() {
  return useMutation<
    WorkflowIntelligenceExplanation,
    Error,
    {
      riskId: number;
      workflowId: number;
    }
  >({
    mutationFn: ({
      riskId,
      workflowId,
    }) =>
      explainRiskResponseWorkflow(
        riskId,
        workflowId
      ),
  });
}