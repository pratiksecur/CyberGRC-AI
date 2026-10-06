import {
  useMutation,
} from "@tanstack/react-query";

import {
  askAIGRCAnalyst,
  type AIGRCAnalystResponse,
} from "@/api/aiGRCAnalyst";

export function useAIGRCAnalyst() {
  return useMutation<
    AIGRCAnalystResponse,
    Error,
    string
  >({
    mutationFn: askAIGRCAnalyst,
  });
}