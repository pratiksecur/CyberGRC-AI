import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createRisk } from "@/api/risks";
import type { CreateRiskRequest } from "@/api/risks";

export function useCreateRisk() {

  const queryClient = useQueryClient();

  return useMutation({

    mutationFn: (
      data: CreateRiskRequest
    ) => createRisk(data),

    onSuccess: () => {

      queryClient.invalidateQueries({
        queryKey: ["risks"],
      });

    },

  });

}