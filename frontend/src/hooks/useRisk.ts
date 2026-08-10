import { useQuery } from "@tanstack/react-query";

import { getRisk } from "@/api/risks";

export function useRisk(id: number) {
  return useQuery({
    queryKey: ["risk", id],
    queryFn: () => getRisk(id),
    enabled: !!id,
  });
}