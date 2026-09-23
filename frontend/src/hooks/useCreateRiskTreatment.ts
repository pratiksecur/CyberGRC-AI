import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createRiskTreatment,
} from "@/api/riskTreatments";

import type {
  CreateRiskTreatmentRequest,
} from "@/api/riskTreatments";


export function useCreateRiskTreatment() {
  const queryClient =
    useQueryClient();

  return useMutation({

    mutationFn: (
      data: CreateRiskTreatmentRequest
    ) =>
      createRiskTreatment(data),

    onSuccess: (_, variables) => {

      queryClient.invalidateQueries({
        queryKey: [
          "risk-treatments",
        ],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "risk-treatments",
          "risk",
          variables.risk_id,
        ],
      });

    },

  });
}