import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createCorrectiveAction,
} from "@/api/correctiveActions";

import type {
  CreateCorrectiveActionRequest,
} from "@/api/correctiveActions";

export function useCreateCorrectiveAction() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      data: CreateCorrectiveActionRequest
    ) =>
      createCorrectiveAction(data),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["corrective-actions"],
      });
    },
  });
}