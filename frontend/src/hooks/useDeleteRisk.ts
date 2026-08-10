import { useMutation, useQueryClient } from "@tanstack/react-query";

import { deleteRisk } from "@/api/risks";

export function useDeleteRisk() {

  const queryClient = useQueryClient();

  return useMutation({

    mutationFn: deleteRisk,

    onSuccess: () => {

      queryClient.invalidateQueries({
        queryKey: ["risks"],
      });

    },

  });

}