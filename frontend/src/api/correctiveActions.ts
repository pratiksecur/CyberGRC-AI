import api from "./axios";

export interface CorrectiveAction {
  id: number;

  finding_id: number;
  finding_title: string;

  assigned_to: number;
  assignee_name: string;

  title: string;
  description: string;

  priority: string;
  status: string;

  due_date: string | null;
  completed_at: string | null;

  comments: string | null;

  created_at: string;
  updated_at: string;
}

export interface CorrectiveActionAssignee {
  id: number;
  name: string;
}

export interface CreateCorrectiveActionRequest {
  finding_id: number;
  assigned_to: number;
  title: string;
  description: string;
  priority: string;
  status: string;
  due_date: string | null;
  completed_at?: string | null;
  comments: string | null;
}

export type UpdateCorrectiveActionRequest =
  Partial<CreateCorrectiveActionRequest>;

export async function getCorrectiveActions(): Promise<
  CorrectiveAction[]
> {
  const response = await api.get(
    "/corrective-actions/"
  );

  return response.data;
}

export async function getCorrectiveAction(
  id: number
): Promise<CorrectiveAction> {
  const response = await api.get(
    `/corrective-actions/${id}`
  );

  return response.data;
}

export async function getCorrectiveActionAssignees(): Promise<
  CorrectiveActionAssignee[]
> {
  const response = await api.get(
    "/corrective-actions/assignees"
  );

  return response.data;
}

export async function createCorrectiveAction(
  data: CreateCorrectiveActionRequest
): Promise<CorrectiveAction> {
  const response = await api.post(
    "/corrective-actions/",
    data
  );

  return response.data;
}

export async function updateCorrectiveAction(
  id: number,
  data: UpdateCorrectiveActionRequest
): Promise<CorrectiveAction> {
  const response = await api.patch(
    `/corrective-actions/${id}`,
    data
  );

  return response.data;
}

export async function deleteCorrectiveAction(
  id: number
): Promise<void> {
  await api.delete(
    `/corrective-actions/${id}`
  );
}