import { useMutation, useQueryClient } from "@tanstack/react-query";

import { createFramework } from "@/api/frameworks";
import type { CreateFrameworkRequest } from "@/api/frameworks";

export function useCreateFramework() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateFrameworkRequest) =>
      createFramework(data),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["frameworks"],
      });
    },
  });
}