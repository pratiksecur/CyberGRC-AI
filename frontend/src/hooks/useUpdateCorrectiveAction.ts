import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  updateCorrectiveAction,
} from "@/api/correctiveActions";

import type {
  UpdateCorrectiveActionRequest,
} from "@/api/correctiveActions";

export function useUpdateCorrectiveAction() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: UpdateCorrectiveActionRequest;
    }) =>
      updateCorrectiveAction(
        id,
        data
      ),

    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["corrective-actions"],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "corrective-action",
          variables.id,
        ],
      });
    },
  });
}