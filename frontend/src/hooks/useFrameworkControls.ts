import { useQuery } from "@tanstack/react-query";

import {
  getFrameworkControls,
} from "@/api/frameworkControls";

export function useFrameworkControls() {
  return useQuery({
    queryKey: ["framework-controls"],
    queryFn: getFrameworkControls,
  });
}