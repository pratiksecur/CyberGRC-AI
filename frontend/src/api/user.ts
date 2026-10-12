import api from "./axios";

export interface CurrentUser {
  id: number;
  full_name: string;
  email: string;
  role: string;
}

export interface VisibleUser {
  id: number;
  full_name: string;
  email: string;
  role: string;
  created_at: string;
}

export interface ManagedUser extends VisibleUser {
  is_active: boolean;
}

export async function getCurrentUser(): Promise<CurrentUser> {
  const response = await api.get("/auth/me");
  return response.data;
}

export async function getVisibleUsers(): Promise<VisibleUser[]> {
  const response = await api.get("/users/visible");
  return response.data;
}

/* ---------------- administrator user management ---------------- */

export async function getAllUsers(): Promise<ManagedUser[]> {
  const response = await api.get("/users/");
  return response.data;
}

export async function deactivateUser(
  userId: number
): Promise<void> {
  await api.post(`/users/${userId}/deactivate`);
}

export async function activateUser(
  userId: number
): Promise<void> {
  await api.post(`/users/${userId}/activate`);
}

export async function resetUserPassword(
  userId: number,
  newPassword: string
): Promise<void> {
  await api.post(`/users/${userId}/reset-password`, {
    new_password: newPassword,
  });
}