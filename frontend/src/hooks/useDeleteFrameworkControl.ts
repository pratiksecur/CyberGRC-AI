import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  deleteFrameworkControl,
} from "@/api/frameworkControls";

export function useDeleteFrameworkControl() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn:
      deleteFrameworkControl,

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["framework-controls"],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "control-framework-controls",
        ],
      });
    },
  });
}