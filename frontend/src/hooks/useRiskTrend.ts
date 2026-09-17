import { useQuery } from "@tanstack/react-query";

import {
  getRiskTrend,
} from "@/api/riskTrend";

import { useAuth } from "@/contexts/useAuth";

export function useRiskTrend() {

  const { user } = useAuth();

  return useQuery({
    queryKey: [
      "risk-trend",
      user?.id,
    ],

    queryFn: getRiskTrend,

    enabled: !!user,
  });
}