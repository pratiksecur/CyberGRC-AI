import { useQuery } from "@tanstack/react-query";

import {
  getExecutiveSummary,
} from "@/api/ai";

export function useExecutiveSummary() {
  return useQuery({
    queryKey: ["executive-summary"],
    queryFn: getExecutiveSummary,
  });
}