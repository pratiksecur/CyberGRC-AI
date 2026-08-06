import { useQuery } from "@tanstack/react-query";
import { getAISummary } from "@/api/ai";

export function useAISummary() {
  return useQuery({
    queryKey: ["ai-summary"],
    queryFn: getAISummary,
  });
}