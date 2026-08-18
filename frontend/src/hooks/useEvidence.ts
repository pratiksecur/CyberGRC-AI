import { useQuery } from "@tanstack/react-query";

import { getEvidence } from "@/api/evidence";

export function useEvidence() {
  return useQuery({
    queryKey: ["evidence"],
    queryFn: getEvidence,
  });
}