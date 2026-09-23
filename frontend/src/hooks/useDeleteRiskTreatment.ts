import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  deleteRiskTreatment,
} from "@/api/riskTreatments";


export function useDeleteRiskTreatment() {
  const queryClient =
    useQueryClient();

  return useMutation({

    mutationFn: deleteRiskTreatment,

    onSuccess: () => {

      queryClient.invalidateQueries({
        queryKey: [
          "risk-treatments",
        ],
      });

    },

  });
}