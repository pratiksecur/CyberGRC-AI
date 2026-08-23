import { useQuery } from "@tanstack/react-query";

import { getComplianceReport } from "@/api/reports";

export function useComplianceReport() {
  return useQuery({
    queryKey: ["compliance-report"],
    queryFn: getComplianceReport,
  });
}