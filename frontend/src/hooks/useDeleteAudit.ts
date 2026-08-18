import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import { deleteAudit } from "@/api/audits";

export function useDeleteAudit() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: deleteAudit,

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["audits"],
      });
    },
  });
}