import api from "./axios";

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
}

export interface RegisterResponse {
  id: number;
  full_name: string;
  email: string;
  role: string;
  created_at: string;
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

export async function register(
  data: RegisterRequest
): Promise<RegisterResponse> {
  const response = await api.post(
    "/auth/register",
    data
  );

  return response.data;
}