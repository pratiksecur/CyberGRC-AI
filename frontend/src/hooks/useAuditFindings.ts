import { useQuery } from "@tanstack/react-query";

import { getAuditFindings } from "@/api/auditFindings";

export function useAuditFindings() {
  return useQuery({
    queryKey: ["audit-findings"],
    queryFn: getAuditFindings,
  });
}