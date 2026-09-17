import { useQuery } from "@tanstack/react-query";

import {
  getExecutiveSummary,
} from "@/api/ai";

import { useAuth } from "@/contexts/useAuth";

import {
  hasPermission,
  type UserRole,
} from "@/auth/permissions";


export function useExecutiveSummary(
  enabled = true
) {

  const { user } = useAuth();

  const role =
    user?.role as UserRole | undefined;

  const canViewExecutiveSummary =
    hasPermission(
      role,
      "ai_executive_summary",
      "view"
    );

  return useQuery({
    queryKey: [
      "executive-summary",
      user?.id,
    ],

    queryFn: getExecutiveSummary,

    enabled:
      !!user &&
      enabled &&
      canViewExecutiveSummary,
  });
}