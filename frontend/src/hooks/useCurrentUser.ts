import { useQuery } from "@tanstack/react-query";
import { getCurrentUser } from "@/api/user";

export function useCurrentUser() {
  return useQuery({
    queryKey: ["current-user"],
    queryFn: getCurrentUser,
  });
}