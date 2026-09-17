import { useQuery } from "@tanstack/react-query";

import {
  getMonitoringOverview,
  getRiskMonitoring,
} from "@/api/monitoring";

import { useAuth } from "@/contexts/useAuth";


// ==========================================================
// MONITORING OVERVIEW
// ==========================================================

export function useMonitoring() {
  const { user } = useAuth();

  return useQuery({
    queryKey: [
      "monitoring",
      user?.id,
    ],

    queryFn:
      getMonitoringOverview,

    enabled: !!user,

    refetchInterval: 60_000,
  });
}


// ==========================================================
// RISK MONITORING
// ==========================================================

export function useRiskMonitoring(
  riskId: number
) {
  return useQuery({
    queryKey: [
      "risk-monitoring",
      riskId,
    ],

    queryFn: () =>
      getRiskMonitoring(riskId),

    enabled: !!riskId,

    refetchInterval: 60_000,
  });
}