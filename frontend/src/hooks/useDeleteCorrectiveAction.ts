import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  deleteCorrectiveAction,
} from "@/api/correctiveActions";

export function useDeleteCorrectiveAction() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: deleteCorrectiveAction,

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["corrective-actions"],
      });
    },
  });
}