import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  updateRiskTreatment,
} from "@/api/riskTreatments";

import type {
  UpdateRiskTreatmentRequest,
} from "@/api/riskTreatments";


export function useUpdateRiskTreatment() {
  const queryClient =
    useQueryClient();

  return useMutation({

    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: UpdateRiskTreatmentRequest;
    }) =>
      updateRiskTreatment(
        id,
        data
      ),

    onSuccess: (treatment) => {

      queryClient.invalidateQueries({
        queryKey: [
          "risk-treatments",
        ],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "risk-treatment",
          treatment.id,
        ],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "risk-treatments",
          "risk",
          treatment.risk_id,
        ],
      });

    },

  });
}