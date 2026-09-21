import { useQuery } from "@tanstack/react-query";

import { getRisksForControl } from "@/api/riskControls";

export function useRisksForControl(
  controlId: number
) {
  return useQuery({
    queryKey: [
      "risk-controls",
      "control",
      controlId,
    ],
    queryFn: () =>
      getRisksForControl(controlId),
    enabled: !!controlId,
  });
}