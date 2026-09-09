import { useQuery } from "@tanstack/react-query";

import {
  getControlsForFrameworkControl,
} from "@/api/controlFrameworkMappings";

export function useControlsForFrameworkControl(
  frameworkControlId: number
) {
  return useQuery({
    queryKey: [
      "control-framework-controls",
      "framework-control",
      frameworkControlId,
    ],
    queryFn: () =>
      getControlsForFrameworkControl(
        frameworkControlId
      ),
    enabled: !!frameworkControlId,
  });
}