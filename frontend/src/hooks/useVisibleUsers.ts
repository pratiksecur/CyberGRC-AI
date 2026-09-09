import { useQuery } from "@tanstack/react-query";

import { getVisibleUsers } from "@/api/user";

export function useVisibleUsers() {
  return useQuery({
    queryKey: ["visible-users"],
    queryFn: getVisibleUsers,
  });
}