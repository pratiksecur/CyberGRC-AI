import { useQuery } from "@tanstack/react-query";

import {
  getCorrectiveActionAssignees,
} from "@/api/correctiveActions";

export function useCorrectiveActionAssignees() {
  return useQuery({
    queryKey: [
      "corrective-action-assignees",
    ],
    queryFn:
      getCorrectiveActionAssignees,
  });
}