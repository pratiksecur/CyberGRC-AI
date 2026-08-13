import api from "./axios";

export interface Control {
  id: number;
  title: string;
  description: string;
  control_type: string;
  status: string;
  effectiveness: number;
  owner_id: number;
  created_at: string;
  updated_at: string;
}

export interface CreateControlRequest {
  title: string;
  description: string;
  control_type: string;
  status: string;
  effectiveness: number;
  owner_id: number;
}

export async function getControls(): Promise<Control[]> {
  const response = await api.get("/controls/");
  return response.data;
}

export async function getControl(
  id: number
): Promise<Control> {
  const response = await api.get(
    `/controls/${id}`
  );

  return response.data;
}

export async function createControl(
  data: CreateControlRequest
): Promise<Control> {
  const response = await api.post(
    "/controls/",
    data
  );

  return response.data;
}

export async function updateControl(
  id: number,
  data: CreateControlRequest
): Promise<Control> {
  const response = await api.patch(
    `/controls/${id}`,
    data
  );

  return response.data;
}

export async function deleteControl(
  id: number
) {
  await api.delete(
    `/controls/${id}`
  );
}