import axios, { AxiosError } from "axios";
import type {
  GraphResponse,
  HealthResponse,
  RegisterPayload,
  TokenResponse,
  UserResponse
} from "./types";

const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:8000/api/v1";

const client = axios.create({
  baseURL: apiBase,
  timeout: 45000
});

const authHeader = (token?: string | null) =>
  token
    ? {
        Authorization: `Bearer ${token}`
      }
    : {};

export const parseApiError = (error: unknown): string => {
  if (error instanceof AxiosError) {
    const detail = (error.response?.data as { detail?: string } | undefined)?.detail;
    if (detail) {
      return detail;
    }
    if (error.message) {
      return error.message;
    }
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Unknown error";
};

export async function healthLive(): Promise<HealthResponse> {
  const response = await client.get<HealthResponse>("/health/live");
  return response.data;
}

export async function healthReady(): Promise<HealthResponse> {
  const response = await client.get<HealthResponse>("/health/ready");
  return response.data;
}

export async function login(username: string, password: string): Promise<TokenResponse> {
  const response = await client.post<TokenResponse>("/auth/login", { username, password });
  return response.data;
}

export async function register(payload: RegisterPayload): Promise<UserResponse> {
  const response = await client.post<UserResponse>("/auth/register", payload);
  return response.data;
}

export async function me(token: string): Promise<UserResponse> {
  const response = await client.get<UserResponse>("/auth/me", { headers: authHeader(token) });
  return response.data;
}

export async function graphExecute(
  token: string,
  userInput: string,
  threadId?: string | null
): Promise<GraphResponse> {
  const response = await client.post<GraphResponse>(
    "/graph/execute",
    {
      user_input: userInput,
      thread_id: threadId || undefined
    },
    {
      headers: authHeader(token)
    }
  );
  return response.data;
}

export async function listUsers(token: string, skip = 0, limit = 50): Promise<UserResponse[]> {
  const response = await client.get<UserResponse[]>(`/admin/users?skip=${skip}&limit=${limit}`, {
    headers: authHeader(token)
  });
  return response.data;
}

export { apiBase };
