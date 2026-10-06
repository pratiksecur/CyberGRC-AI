import { useQuery } from "@tanstack/react-query";

import {
  getControlIntelligence,
} from "@/api/controls";

export function useControlIntelligence() {
  return useQuery({
    queryKey: [
      "control-intelligence",
    ],

    queryFn:
      getControlIntelligence,

    refetchInterval: 60000,
  });
}