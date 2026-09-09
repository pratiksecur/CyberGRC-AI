import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createControlFrameworkMapping,
} from "@/api/controlFrameworkMappings";

import type {
  CreateControlFrameworkMappingRequest,
} from "@/api/controlFrameworkMappings";

export function useCreateControlFrameworkMapping() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      data: CreateControlFrameworkMappingRequest
    ) =>
      createControlFrameworkMapping(
        data
      ),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [
          "control-framework-controls",
        ],
      });
    },
  });
}