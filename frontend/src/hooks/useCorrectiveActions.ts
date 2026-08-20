import { useQuery } from "@tanstack/react-query";

import {
  getCorrectiveActions,
} from "@/api/correctiveActions";

export function useCorrectiveActions() {
  return useQuery({
    queryKey: ["corrective-actions"],
    queryFn: getCorrectiveActions,
  });
}