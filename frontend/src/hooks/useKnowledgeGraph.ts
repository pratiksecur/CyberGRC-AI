import { useQuery } from "@tanstack/react-query";

import {
  getKnowledgeGraph,
} from "@/api/intelligence";


export function useKnowledgeGraph(
  riskId?: number
) {
  return useQuery({
    queryKey: [
      "knowledge-graph",
      riskId ?? null,
    ],

    queryFn: () =>
      getKnowledgeGraph(
        riskId
      ),
  });
}