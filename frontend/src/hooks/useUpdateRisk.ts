import { useMutation, useQueryClient } from "@tanstack/react-query";

import { updateRisk } from "@/api/risks";
import type { CreateRiskRequest } from "@/api/risks";

export function useUpdateRisk(id: number) {

  const queryClient = useQueryClient();

  return useMutation({

    mutationFn: (data: CreateRiskRequest) =>
      updateRisk(id, data),

    onSuccess: () => {

      queryClient.invalidateQueries({
        queryKey: ["risks"],
      });

      queryClient.invalidateQueries({
        queryKey: ["risk", id],
      });

    },

  });

}