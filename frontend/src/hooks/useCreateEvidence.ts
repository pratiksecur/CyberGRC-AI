import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createEvidence } from "@/api/evidence";
import type { CreateEvidenceRequest } from "@/api/evidence";

export function useCreateEvidence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: FormData) =>
      createEvidence(data),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["evidence"],
      });
    },
  });
}