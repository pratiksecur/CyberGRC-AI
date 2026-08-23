import { useQuery } from "@tanstack/react-query";

import { getAuditReport } from "@/api/reports";

export function useAuditReport() {
  return useQuery({
    queryKey: ["audit-report"],
    queryFn: getAuditReport,
  });
}