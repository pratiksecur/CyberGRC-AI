import api from "@/api/axios";

export interface ExecutiveIntelligence {
  risk_posture: {
    level: string;
    total: number;
    critical: number;
    high: number;
    average_score: number;
    distribution: {
      critical: number;
      high: number;
      moderate: number;
      low: number;
    };
  };

  compliance_posture: {
    level: string;
    score: number;
    active_controls: number;
    controls_without_evidence: number;
    stale_evidence: number;
  };

  control_health: {
    total: number;
    active: number;
    healthy: number;
    degraded: number;
    ineffective: number;
    average_effectiveness: number;
  };

  regulatory_exposure: {
    framework_count: number;
    frameworks: Record<
      string,
      {
        control_count: number;
        exposure: string;
      }
    >;
  };

  findings: {
    total: number;
    open: number;
    critical_open: number;
  };

  remediation: {
    total_actions: number;
    open_actions: number;
    overdue_actions: number;
  };

  treatment_effectiveness: {
    total: number;
    active: number;
    overdue: number;
    with_residual_risk: number;
    elevated_residual_risk: number;
  };

  workflow_health: {
    total: number;
    open: number;
    completed: number;
    blocked: number;
    escalated: number;
  };

  regulatory: {
    framework_count: number;
    frameworks: Record<
      string,
      {
        control_count: number;
        exposure: string;
      }
    >;
  };

  business_unit_exposure: Array<{
    owner_id: number;
    owner_name: string;
    risk_count: number;
    critical_risks: number;
    high_risks: number;
    max_risk_score: number;
  }>;

  explainability: Array<{
    signal: string;
    severity: string;
    count: number;
    why: string;
  }>;

  scope: {
    visible_user_count: number;
    risk_count: number;
    control_count: number;
    evidence_count: number;
  };

  generated_at: string;
}

export async function getExecutiveIntelligence(): Promise<ExecutiveIntelligence> {
  const response = await api.get<ExecutiveIntelligence>(
    "/intelligence/executive",
  );

  return response.data;
}