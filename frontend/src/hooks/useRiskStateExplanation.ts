import { useMutation } from "@tanstack/react-query";

import {
  explainRiskState,
  type RiskStateExplanation,
} from "@/api/ai";

export function useRiskStateExplanation() {
  return useMutation<RiskStateExplanation, Error, number>({
    mutationFn: (riskId: number) =>
      explainRiskState(riskId),
  });
}