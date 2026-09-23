import { useQuery } from "@tanstack/react-query";

import {
  getRiskTreatment,
} from "@/api/riskTreatments";


export function useRiskTreatment(
  id: number
) {
  return useQuery({
    queryKey: [
      "risk-treatment",
      id,
    ],

    queryFn: () =>
      getRiskTreatment(id),

    enabled: !!id,
  });
}