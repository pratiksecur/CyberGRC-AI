import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import { updateAudit } from "@/api/audits";
import type { CreateAuditRequest } from "@/api/audits";

export function useUpdateAudit(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (
      data: Partial<CreateAuditRequest>
    ) => updateAudit(id, data),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["audits"],
      });

      queryClient.invalidateQueries({
        queryKey: ["audit", id],
      });
    },
  });
}