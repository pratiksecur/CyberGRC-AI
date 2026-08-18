import api from "./axios";

export interface Evidence {
  id: number;
  control_id: number;
  title: string;
  description: string;
  file_name: string;
  file_path: string;
  uploaded_by: number;
  uploaded_at: string;
}

export interface CreateEvidenceRequest {
  control_id: number;
  title: string;
  description: string;
  file_name: string;
  file_path: string;
  uploaded_by: number;
}

export async function getEvidence(): Promise<Evidence[]> {
  const response = await api.get("/evidence/");
  return response.data;
}

export async function getEvidenceById(
  id: number
): Promise<Evidence> {
  const response = await api.get(
    `/evidence/${id}`
  );

  return response.data;
}

export async function createEvidence(
  data: FormData
): Promise<Evidence> {
  const response = await api.post(
    "/evidence/",
    data,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
}

export async function updateEvidence(
  id: number,
  data: Partial<CreateEvidenceRequest>
): Promise<Evidence> {
  const response = await api.patch(
    `/evidence/${id}`,
    data
  );

  return response.data;
}

export async function deleteEvidence(
  id: number
) {
  await api.delete(`/evidence/${id}`);
}