import { useQuery } from "@tanstack/react-query";

import { getAuditFinding } from "@/api/auditFindings";

export function useAuditFinding(
  id: number
) {
  return useQuery({
    queryKey: ["audit-finding", id],
    queryFn: () =>
      getAuditFinding(id),
    enabled: !!id,
  });
}