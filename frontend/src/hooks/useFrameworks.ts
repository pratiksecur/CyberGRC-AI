import { useQuery } from "@tanstack/react-query";

import { getFrameworks } from "@/api/frameworks";

export function useFrameworks() {
  return useQuery({
    queryKey: ["frameworks"],
    queryFn: getFrameworks,
  });
}