import { useQuery } from "@tanstack/react-query";

import {
  getGRCIntelligenceOverview,
  getRiskIntelligence,
} from "@/api/intelligence";

import { useAuth } from "@/contexts/useAuth";


// ==========================================================
// OVERVIEW
// ==========================================================

export function useGRCIntelligence() {
  const { user } = useAuth();

  return useQuery({
    queryKey: [
      "grc-intelligence",
      user?.id,
    ],

    queryFn:
      getGRCIntelligenceOverview,

    enabled: !!user,

    refetchInterval: 60_000,
  });
}


// ==========================================================
// RISK INTELLIGENCE
// ==========================================================

export function useRiskIntelligence(
  riskId: number
) {
  return useQuery({
    queryKey: [
      "risk-intelligence",
      riskId,
    ],

    queryFn: () =>
      getRiskIntelligence(riskId),

    enabled: !!riskId,

    refetchInterval: 60_000,
  });
}