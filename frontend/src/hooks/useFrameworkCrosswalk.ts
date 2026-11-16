import { useQuery } from "@tanstack/react-query";

import {
  getCrosswalkOpportunities,
  getCrosswalkSuggestions,
  getRelatedRequirements,
} from "@/api/frameworkCrosswalk";

/*
 * Every key starts with "control-framework-controls", the same prefix the
 * mapping mutations invalidate. Creating or removing a mapping therefore
 * refreshes the crosswalk results without any extra wiring.
 */

const BASE_KEY = "control-framework-controls";

export function useCrosswalkSuggestions(controlId: number) {
  return useQuery({
    queryKey: [BASE_KEY, "crosswalk", "control", controlId],
    queryFn: () => getCrosswalkSuggestions(controlId),
    enabled: !!controlId,
  });
}

export function useRelatedRequirements(frameworkControlId: number) {
  return useQuery({
    queryKey: [
      BASE_KEY,
      "crosswalk",
      "framework-control",
      frameworkControlId,
    ],
    queryFn: () => getRelatedRequirements(frameworkControlId),
    enabled: !!frameworkControlId,
  });
}

export function useCrosswalkOpportunities() {
  return useQuery({
    queryKey: [BASE_KEY, "crosswalk", "opportunities"],
    queryFn: getCrosswalkOpportunities,
  });
}
