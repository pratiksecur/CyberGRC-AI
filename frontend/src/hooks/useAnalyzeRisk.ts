import { useMutation } from "@tanstack/react-query";

import { analyzeRisk } from "@/api/ai";

export function useAnalyzeRisk() {
  return useMutation({
    mutationFn: (riskId: number) =>
      analyzeRisk(riskId),
  });
}