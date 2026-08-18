import api from "./axios";

export interface Audit {
  id: number;
  name: string;
  framework_id: number;
  auditor_id: number;
  scope: string;
  status: string;
  start_date: string;
  end_date: string;
  created_at: string;
  updated_at: string;
}

export interface CreateAuditRequest {
  name: string;
  framework_id: number;
  auditor_id: number;
  scope: string;
  status: string;
  start_date: string;
  end_date: string;
}

export async function getAudits(): Promise<Audit[]> {
  const response = await api.get("/audits/");
  return response.data;
}

export async function getAudit(
  id: number
): Promise<Audit> {
  const response = await api.get(
    `/audits/${id}`
  );

  return response.data;
}

export async function createAudit(
  data: CreateAuditRequest
): Promise<Audit> {
  const response = await api.post(
    "/audits/",
    data
  );

  return response.data;
}

export async function updateAudit(
  id: number,
  data: Partial<CreateAuditRequest>
): Promise<Audit> {
  const response = await api.patch(
    `/audits/${id}`,
    data
  );

  return response.data;
}

export async function deleteAudit(
  id: number
) {
  await api.delete(
    `/audits/${id}`
  );
}