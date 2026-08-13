import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  createControl,
  CreateControlRequest,
} from "@/api/controls";

export function useCreateControl() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateControlRequest) =>
      createControl(data),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["controls"],
      });
    },
  });
}