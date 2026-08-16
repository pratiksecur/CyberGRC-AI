import { useMutation, useQueryClient } from "@tanstack/react-query";

import { updateControl } from "@/api/controls";
import type { CreateControlRequest } from "@/api/controls";

export function useUpdateControl(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateControlRequest) =>
      updateControl(id, data),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["controls"],
      });

      queryClient.invalidateQueries({
        queryKey: ["control", id],
      });
    },
  });
}