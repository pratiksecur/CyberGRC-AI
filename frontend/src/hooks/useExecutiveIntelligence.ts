import { useQuery } from "@tanstack/react-query";

import {
  getExecutiveIntelligence,
  type ExecutiveIntelligence,
} from "@/api/executiveIntelligence";

export function useExecutiveIntelligence() {
  return useQuery<ExecutiveIntelligence>({
    queryKey: ["executive-intelligence"],
    queryFn: getExecutiveIntelligence,
    staleTime: 60 * 1000,
  });
}