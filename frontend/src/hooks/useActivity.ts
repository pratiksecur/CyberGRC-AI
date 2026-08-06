import { useQuery } from "@tanstack/react-query";
import { getRecentActivity } from "@/api/activity";

export function useActivity() {
  return useQuery({
    queryKey: ["activity"],
    queryFn: getRecentActivity,
  });
}