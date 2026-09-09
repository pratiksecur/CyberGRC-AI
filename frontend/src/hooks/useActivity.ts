import { useQuery } from "@tanstack/react-query";

import {
  getRecentActivity,
} from "@/api/activity";

import { useAuth } from "@/contexts/AuthContext";

export function useActivity() {

  const { user } = useAuth();

  return useQuery({
    queryKey: [
      "activity",
      user?.id,
    ],

    queryFn: getRecentActivity,

    enabled: !!user,
  });
}