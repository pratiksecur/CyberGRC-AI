import { useMutation } from "@tanstack/react-query";

import {
  recommendControls,
} from "@/api/ai";

export function useRecommendControls() {
  return useMutation({
    mutationFn: (riskId: number) =>
      recommendControls(riskId),
  });
}