import { useQuery } from "@tanstack/react-query";

import {
  getCorrectiveActionReport,
} from "@/api/reports";

export function useCorrectiveActionReport() {
  return useQuery({
    queryKey: ["corrective-action-report"],
    queryFn: getCorrectiveActionReport,
  });
}