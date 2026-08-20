import api from "./axios";

export interface CriticalRemediation {
  findingTitle: string;
  findingSeverity: string;

  actionTitle: string;
  assigneeName: string;

  priority: string;
  status: string;

  dueDate: string;
}

export interface CriticalRemediation {
  findingId: number;
  findingTitle: string;
  findingSeverity: string;

  actionId: number;
  actionTitle: string;

  assigneeName: string;
  priority: string;
  status: string;
  dueDate: string;
}

export interface DashboardResponse {
  totalRisks: number;
  controls: number;
  audits: number;

  compliance: number;
  securityHealth: number;

  criticalRisks: number;
  activeControls: number;

  totalFindings: number;
  openFindings: number;
  criticalFindings: number;

  totalActions: number;
  pendingActions: number;
  overdueActions: number;

  criticalRemediation: CriticalRemediation | null;
}

export const getDashboard = async (): Promise<DashboardResponse> => {
  const response = await api.get("/dashboard");

  return response.data;
};