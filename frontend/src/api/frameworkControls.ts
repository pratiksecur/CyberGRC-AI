import api from "./axios";

export interface FrameworkControl {
  id: number;
  framework_id: number;
  control_code: string;
  title: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface CreateFrameworkControlRequest {
  framework_id: number;
  control_code: string;
  title: string;
  description: string;
}

export interface UpdateFrameworkControlRequest {
  control_code?: string;
  title?: string;
  description?: string;
}

export async function getFrameworkControls(): Promise<
  FrameworkControl[]
> {
  const response = await api.get(
    "/framework-controls/"
  );

  return response.data;
}

export async function getFrameworkControl(
  id: number
): Promise<FrameworkControl> {
  const response = await api.get(
    `/framework-controls/${id}`
  );

  return response.data;
}

export async function createFrameworkControl(
  data: CreateFrameworkControlRequest
): Promise<FrameworkControl> {
  const response = await api.post(
    "/framework-controls/",
    data
  );

  return response.data;
}

export async function updateFrameworkControl(
  id: number,
  data: UpdateFrameworkControlRequest
): Promise<FrameworkControl> {
  const response = await api.patch(
    `/framework-controls/${id}`,
    data
  );

  return response.data;
}

export async function deleteFrameworkControl(
  id: number
): Promise<void> {
  await api.delete(
    `/framework-controls/${id}`
  );
}