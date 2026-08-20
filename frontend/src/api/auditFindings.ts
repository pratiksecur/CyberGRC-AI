import api from "./axios";

export interface AuditFinding {
  id: number;

  audit_id: number;
  audit_name: string;

  control_id: number;
  control_name: string;

  title: string;
  description: string;

  severity: string;

  recommendation: string;

  status: string;

  created_at: string;
  updated_at: string;
}

export interface CreateAuditFindingRequest {
  audit_id: number;
  control_id: number;

  title: string;
  description: string;

  severity: string;

  recommendation: string;

  status: string;
}

export async function getAuditFindings(): Promise<
  AuditFinding[]
> {
  const response = await api.get(
    "/audit-findings/"
  );

  return response.data;
}


export async function getAuditFinding(
  id: number
): Promise<AuditFinding> {
  const response = await api.get(
    `/audit-findings/${id}`
  );

  return response.data;
}


export async function createAuditFinding(
  data: CreateAuditFindingRequest
): Promise<AuditFinding> {
  const response = await api.post(
    "/audit-findings/",
    data
  );

  return response.data;
}


export async function updateAuditFinding(
  id: number,
  data: Partial<CreateAuditFindingRequest>
): Promise<AuditFinding> {
  const response = await api.patch(
    `/audit-findings/${id}`,
    data
  );

  return response.data;
}


export async function deleteAuditFinding(
  id: number
) {
  await api.delete(
    `/audit-findings/${id}`
  );
}