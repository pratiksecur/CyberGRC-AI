import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  updateFrameworkControl,
} from "@/api/frameworkControls";

import type {
  UpdateFrameworkControlRequest,
} from "@/api/frameworkControls";

export function useUpdateFrameworkControl(
  id: number
) {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      data: UpdateFrameworkControlRequest
    ) =>
      updateFrameworkControl(
        id,
        data
      ),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["framework-controls"],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "framework-controls",
          id,
        ],
      });
    },
  });
}