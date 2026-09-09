import { useQuery } from "@tanstack/react-query";

import {
  getFrameworkControl,
} from "@/api/frameworkControls";

export function useFrameworkControl(
  id: number
) {
  return useQuery({
    queryKey: ["framework-controls", id],
    queryFn: () =>
      getFrameworkControl(id),
    enabled: !!id,
  });
}