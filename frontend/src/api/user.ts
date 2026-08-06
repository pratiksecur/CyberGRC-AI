import api from "./axios";

export interface CurrentUser {
  id: number;
  full_name: string;
  email: string;
  role: string;
}

export async function getCurrentUser(): Promise<CurrentUser> {
  const response = await api.get("/auth/me");
  return response.data;
}