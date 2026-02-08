export type TokenResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
  roles: string[];
  permissions: string[];
};

export type UserResponse = {
  id: number;
  username: string;
  real_name: string | null;
  email: string | null;
  phone: string | null;
  passenger_id: string | null;
  is_active: boolean;
  roles: string[];
  permissions: string[];
};

export type RegisterPayload = {
  username: string;
  password: string;
  real_name?: string;
  email?: string;
  phone?: string;
  passenger_id?: string;
};

export type GraphResponse = {
  assistant: string;
  thread_id: string;
  interrupted: boolean;
};

export type HealthResponse = {
  status: string;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant" | "system";
  text: string;
  createdAt: string;
  interrupted?: boolean;
};
