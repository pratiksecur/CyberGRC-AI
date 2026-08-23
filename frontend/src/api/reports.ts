import api from "./axios";

// ==========================================================
// Corrective Actions Report
// ==========================================================

export interface CorrectiveActionReportSummary {
  total_actions: number;
  open_actions: number;
  in_progress_actions: number;
  completed_actions: number;
  closed_actions: number;
  overdue_actions: number;
  critical_actions: number;
  high_actions: number;
}

export interface CorrectiveActionReportItem {
  id: number;

  finding_id: number;
  finding_title: string;

  assigned_to: number;
  assignee_name: string;

  title: string;
  description: string;

  priority: string;
  status: string;

  due_date: string;
  completed_at: string | null;

  comments: string | null;

  created_at: string;
  updated_at: string;

  overdue: boolean;
}

export interface CorrectiveActionReport {
  summary: CorrectiveActionReportSummary;
  actions: CorrectiveActionReportItem[];
}

export async function getCorrectiveActionReport(): Promise<CorrectiveActionReport> {
  const response = await api.get(
    "/reports/corrective-actions/"
  );

  return response.data;
}


// ==========================================================
// Risk Report
// ==========================================================

export interface RiskReportSummary {
  total_risks: number;
  critical_risks: number;
  high_risks: number;
  medium_risks: number;
  low_risks: number;

  open_risks: number;
  closed_risks: number;

  average_risk_score: number;
}

export interface RiskReportItem {
  id: number;

  title: string;
  description: string;

  likelihood: number;
  impact: number;
  risk_score: number;

  status: string;

  owner_id: number;
  owner_name: string;

  created_at: string;
}

export interface RiskReport {
  summary: RiskReportSummary;
  risks: RiskReportItem[];
}

export async function getRiskReport(): Promise<RiskReport> {
  const response = await api.get(
    "/reports/risks/"
  );

  return response.data;
}

// ==========================================================
// Audit Report
// ==========================================================

export interface AuditReportSummary {
  total_audits: number;

  planned_audits: number;
  in_progress_audits: number;
  completed_audits: number;

  total_findings: number;

  critical_findings: number;
  high_findings: number;
  medium_findings: number;
  low_findings: number;

  open_findings: number;
  closed_findings: number;
}

export interface AuditReportItem {
  id: number;

  name: string;

  framework_id: number;
  framework_name: string;

  auditor_id: number;
  auditor_name: string;

  scope: string;

  status: string;

  start_date: string;
  end_date: string;

  finding_count: number;
  critical_finding_count: number;
  open_finding_count: number;

  created_at: string;
}

export interface AuditReport {
  summary: AuditReportSummary;
  audits: AuditReportItem[];
}

export async function getAuditReport(): Promise<AuditReport> {
  const response = await api.get(
    "/reports/audits/"
  );

  return response.data;
}


// ==========================================================
// Compliance Report
// ==========================================================

export interface ComplianceReportSummary {
  total_frameworks: number;

  total_controls: number;
  active_controls: number;

  average_control_effectiveness: number;

  total_evidence: number;

  total_findings: number;
  open_findings: number;
  critical_findings: number;
}

export interface ComplianceReportItem {
  id: number;

  name: string;
  version: string;

  control_count: number;
  active_control_count: number;

  average_effectiveness: number;

  evidence_count: number;

  finding_count: number;
  critical_finding_count: number;
  open_finding_count: number;
}

export interface ComplianceReport {
  summary: ComplianceReportSummary;
  frameworks: ComplianceReportItem[];
}

export async function getComplianceReport(): Promise<ComplianceReport> {
  const response = await api.get(
    "/reports/compliance/"
  );

  return response.data;
}