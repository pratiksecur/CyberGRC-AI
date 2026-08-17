import api from "./axios";

export interface Framework {
  id: number;
  name: string;
  version: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface CreateFrameworkRequest {
  name: string;
  version: string;
  description: string;
}

export async function getFrameworks(): Promise<Framework[]> {
  const response = await api.get("/frameworks/");
  return response.data;
}

export async function getFramework(
  id: number
): Promise<Framework> {
  const response = await api.get(
    `/frameworks/${id}`
  );

  return response.data;
}

export async function createFramework(
  data: CreateFrameworkRequest
): Promise<Framework> {
  const response = await api.post(
    "/frameworks/",
    data
  );

  return response.data;
}

export async function updateFramework(
  id: number,
  data: CreateFrameworkRequest
): Promise<Framework> {
  const response = await api.patch(
    `/frameworks/${id}`,
    data
  );

  return response.data;
}

export async function deleteFramework(
  id: number
) {
  await api.delete(
    `/frameworks/${id}`
  );
}