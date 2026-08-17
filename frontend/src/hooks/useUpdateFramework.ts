import { useMutation, useQueryClient } from "@tanstack/react-query";

import { updateFramework } from "@/api/frameworks";
import type { CreateFrameworkRequest } from "@/api/frameworks";

export function useUpdateFramework(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateFrameworkRequest) =>
      updateFramework(id, data),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["frameworks"],
      });

      queryClient.invalidateQueries({
        queryKey: ["frameworks", id],
      });
    },
  });
}