import { useQuery } from "@tanstack/react-query";

import { getAudit } from "@/api/audits";

export function useAudit(id: number) {
  return useQuery({
    queryKey: ["audit", id],
    queryFn: () => getAudit(id),
    enabled: !!id,
  });
}