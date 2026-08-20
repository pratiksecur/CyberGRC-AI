import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  deleteAuditFinding,
} from "@/api/auditFindings";

export function useDeleteAuditFinding() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: deleteAuditFinding,

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["audit-findings"],
      });
    },
  });
}