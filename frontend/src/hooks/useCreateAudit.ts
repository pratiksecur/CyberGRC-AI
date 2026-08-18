import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import { createAudit } from "@/api/audits";
import type { CreateAuditRequest } from "@/api/audits";

export function useCreateAudit() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      data: CreateAuditRequest
    ) => createAudit(data),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["audits"],
      });
    },
  });
}