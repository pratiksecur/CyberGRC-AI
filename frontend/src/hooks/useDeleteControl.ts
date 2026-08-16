import { useMutation, useQueryClient } from "@tanstack/react-query";

import { deleteControl } from "@/api/controls";

export function useDeleteControl() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => deleteControl(id),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["controls"],
      });
    },
  });
}