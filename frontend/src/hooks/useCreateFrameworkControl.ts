import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createFrameworkControl,
} from "@/api/frameworkControls";

import type {
  CreateFrameworkControlRequest,
} from "@/api/frameworkControls";

export function useCreateFrameworkControl() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      data: CreateFrameworkControlRequest
    ) =>
      createFrameworkControl(data),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["framework-controls"],
      });

      queryClient.invalidateQueries({
        queryKey: ["frameworks"],
      });
    },
  });
}