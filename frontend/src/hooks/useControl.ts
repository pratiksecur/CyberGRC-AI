import { useQuery } from "@tanstack/react-query";

import { getControl } from "@/api/controls";

export function useControl(id: number) {
  return useQuery({
    queryKey: ["control", id],
    queryFn: () => getControl(id),
    enabled: !!id,
  });
}