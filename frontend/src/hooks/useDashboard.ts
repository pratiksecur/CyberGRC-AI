import { useQuery } from "@tanstack/react-query";

import { getDashboard } from "@/api/dashboard";
import { useAuth } from "@/contexts/AuthContext";

export function useDashboard() {

  const { user } = useAuth();

  return useQuery({
    queryKey: [
      "dashboard",
      user?.id,
    ],

    queryFn: getDashboard,

    enabled: !!user,
  });
}