import { useMutation, useQueryClient } from "@tanstack/react-query";

import { updateEvidence } from "@/api/evidence";
import type { CreateEvidenceRequest } from "@/api/evidence";

export function useUpdateEvidence(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (
      data: Partial<CreateEvidenceRequest>
    ) => updateEvidence(id, data),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["evidence"],
      });

      queryClient.invalidateQueries({
        queryKey: ["evidence", id],
      });
    },
  });
}