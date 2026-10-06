import { useQuery } from "@tanstack/react-query";

import {
  getAuditAssurance,
} from "@/api/auditAssurance";


export function useAuditAssurance() {
  return useQuery({
    queryKey: [
      "audit-assurance",
    ],

    queryFn:
      getAuditAssurance,

    refetchInterval: 60_000,
  });
}