import { useQuery } from "@tanstack/react-query";

import {
  getCorrectiveAction,
} from "@/api/correctiveActions";

export function useCorrectiveAction(
  id: number
) {
  return useQuery({
    queryKey: ["corrective-action", id],
    queryFn: () =>
      getCorrectiveAction(id),
    enabled: !!id,
  });
}