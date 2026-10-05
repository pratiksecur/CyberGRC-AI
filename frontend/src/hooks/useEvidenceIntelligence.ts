import { useQuery } from "@tanstack/react-query";

import {
  getEvidenceIntelligence,
} from "@/api/evidence";


export function useEvidenceIntelligence() {
  return useQuery({
    queryKey: [
      "evidence-intelligence",
    ],

    queryFn:
      getEvidenceIntelligence,

    refetchInterval: 60_000,
  });
}