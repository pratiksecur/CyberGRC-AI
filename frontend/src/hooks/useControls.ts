import { useQuery } from "@tanstack/react-query";

import { getControls } from "@/api/controls";

export function useControls() {
  return useQuery({
    queryKey: ["controls"],
    queryFn: getControls,
  });
}