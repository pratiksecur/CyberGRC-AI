import api from "@/api/axios";


export interface AuditAssuranceAudit {
  id: number;

  name: string;

  status: string;

  start_date: string;

  end_date: string;

  overdue: boolean;

  planning_complete: boolean;

  finding_count: number;

  open_findings: number;

  critical_findings: number;

  control_count: number;

  controls_with_evidence: number;

  controls_without_evidence: number;

  corrective_action_count: number;

  open_corrective_actions: number;

  overdue_corrective_actions: number;

  completed_corrective_actions: number;

  closure_ready: boolean;

  closure_blockers: string[];
}


export interface AuditAssurance {
  generated_at: string;

  portfolio: {
    total_audits: number;

    planned: number;

    in_progress: number;

    completed: number;

    overdue: number;

    closure_ready: number;

    blocked: number;
  };

  planning: {
    complete: number;

    incomplete: number;

    completion_percent: number;
  };

  testing: {
    audits_with_findings: number;

    total_findings: number;

    open_findings: number;

    critical_findings: number;

    controls_referenced: number;
  };

  evidence: {
    controls_referenced: number;

    controls_with_evidence: number;

    controls_without_evidence: number;

    coverage_percent: number;
  };

  remediation: {
    total_actions: number;

    open_actions: number;

    completed_actions: number;

    overdue_actions: number;
  };

  closure: {
    ready: number;

    not_ready: number;

    blocked: number;
  };

  assurance_signals: Array<{
    signal: string;

    severity: string;

    count: number;

    why: string;
  }>;

  audits: AuditAssuranceAudit[];

  scope: {
    visible_audit_users: number;

    visible_finding_users: number;

    visible_action_users: number;

    visible_evidence_users: number;

    audit_count: number;
  };
}


export async function getAuditAssurance(): Promise<AuditAssurance> {
  const response =
    await api.get<AuditAssurance>(
      "/intelligence/audit-assurance",
    );

  return response.data;
}