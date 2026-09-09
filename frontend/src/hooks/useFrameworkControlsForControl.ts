import { useQuery } from "@tanstack/react-query";

import {
  getFrameworkControlsForControl,
} from "@/api/controlFrameworkMappings";

export function useFrameworkControlsForControl(
  controlId: number
) {
  return useQuery({
    queryKey: [
      "control-framework-controls",
      "control",
      controlId,
    ],
    queryFn: () =>
      getFrameworkControlsForControl(
        controlId
      ),
    enabled: !!controlId,
  });
}