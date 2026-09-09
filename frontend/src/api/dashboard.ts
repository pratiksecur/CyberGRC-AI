import api from "./axios";

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

  criticalRisks: number;

  controls: number;

  activeControls: number;

  totalEvidence: number;

  audits: number;

  compliance: number;

  securityHealth: number;

  totalFindings: number;

  openFindings: number;

  criticalFindings: number;

  totalActions: number;

  pendingActions: number;

  overdueActions: number;

  criticalRemediation:
    | CriticalRemediation
    | null;
}

export const getDashboard =
  async (): Promise<DashboardResponse> => {

    const response =
      await api.get("/dashboard");

    return response.data;
  };