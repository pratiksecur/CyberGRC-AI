import api from "./axios";

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
  role?: string;
}

export interface RegisterResponse {
  id: number;
  full_name: string;
  email: string;
  role: string;
  created_at: string;
}

export interface CurrentUser {
  id: number;
  full_name: string;
  email: string;
  role: string;
}

export async function login(
  email: string,
  password: string
): Promise<LoginResponse> {
  const formData = new URLSearchParams();

  formData.append("username", email);
  formData.append("password", password);

  const response = await api.post(
    "/auth/login",
    formData,
    {
      headers: {
        "Content-Type":
          "application/x-www-form-urlencoded",
      },
    }
  );

  return response.data;
}

export async function getCurrentUser(): Promise<CurrentUser> {
  const response = await api.get("/auth/me");

  return response.data;
}

export async function getCsrfToken(): Promise<string> {
  const response = await api.get("/auth/csrf");

  return response.data.csrf_token;
}

export async function logout(): Promise<void> {
  await api.post("/auth/logout");
}

export async function register(
  data: RegisterRequest
): Promise<RegisterResponse> {
  const response = await api.post(
    "/auth/register",
    data
  );

  return response.data;
}