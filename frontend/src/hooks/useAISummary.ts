import { useQuery } from "@tanstack/react-query";
import { getExecutiveSummary } from "@/api/ai";

export function useAISummary() {
  return useQuery({
    queryKey: ["ai-summary"],
    queryFn: getExecutiveSummary,
  });
}