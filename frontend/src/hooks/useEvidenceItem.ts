import { useQuery } from "@tanstack/react-query";

import { getEvidenceById } from "@/api/evidence";

export function useEvidenceItem(id: number) {
  return useQuery({
    queryKey: ["evidence", id],
    queryFn: () => getEvidenceById(id),
    enabled: !!id,
  });
}