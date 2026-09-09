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

export async function getCurrentUser(): Promise<CurrentUser> {
  const response = await api.get("/auth/me");
  return response.data;
}

export async function getVisibleUsers(): Promise<VisibleUser[]> {
  const response = await api.get("/users/visible");
  return response.data;
}