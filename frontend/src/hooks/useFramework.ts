import { useQuery } from "@tanstack/react-query";

import { getFramework } from "@/api/frameworks";

export function useFramework(id: number) {
  return useQuery({
    queryKey: ["frameworks", id],
    queryFn: () => getFramework(id),
    enabled: !!id,
  });
}