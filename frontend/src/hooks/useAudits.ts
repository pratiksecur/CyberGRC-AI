import { useQuery } from "@tanstack/react-query";

import { getAudits } from "@/api/audits";

export function useAudits() {
  return useQuery({
    queryKey: ["audits"],
    queryFn: getAudits,
  });
}