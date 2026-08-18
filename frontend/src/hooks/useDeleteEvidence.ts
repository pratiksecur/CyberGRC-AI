import { useMutation, useQueryClient } from "@tanstack/react-query";

import { deleteEvidence } from "@/api/evidence";

export function useDeleteEvidence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteEvidence,

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["evidence"],
      });
    },
  });
}