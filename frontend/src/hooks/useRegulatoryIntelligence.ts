import { useQuery } from "@tanstack/react-query";

import {
  getRegulatoryIntelligence,
} from "@/api/frameworks";

export function useRegulatoryIntelligence() {
  return useQuery({
    queryKey: [
      "regulatory-intelligence",
    ],
    queryFn:
      getRegulatoryIntelligence,
    refetchInterval: 60000,
  });
}