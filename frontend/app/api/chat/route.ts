//src/app/api/routes.ts
import axios, { AxiosResponse } from "axios";

// -----------------------------------------------------------------------------
// Base URL – change once if you move the backend
// -----------------------------------------------------------------------------
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
console.log("API Base URL being used:", API_BASE);

// -----------------------------------------------------------------------------
// DTOs – mirror Java backend DTOs
// -----------------------------------------------------------------------------
export interface UserDTO {
  id: string;
  username: string;
  email: string;
}

export interface CreateUserRequest {
  username: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface JwtResponse {
  token: string;
  username: string;
  userId: string;
}

export interface UpdateUserRequest {
  username: string;
  email: string;
  password?: string;

}

export interface ConversationDTO {
  id: string;
  title: string;
  createdAt: string;
  messages: MessageDTO[];
}

export interface CreateConvRequest {
  userId: string;
  title: string;
}

export interface MessageDTO {
  id: string;
  role: "USER" | "AI";
  content: string;
  sentAt: string;
}

export interface CreateMessageRequest {
  convId: string;
  role: "USER" | "AI";
  content: string;
}

export interface AiRequest {
  prompt: string;
}

export interface AiResponse {
  message: string;
}

// -----------------------------------------------------------------------------
// Axios client
// -----------------------------------------------------------------------------
const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
  timeout: 0, // SSE needs no timeout
});

// Request log + JWT Injection
api.interceptors.request.use(
  (config) => {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    if (token) config.headers.Authorization = `Bearer ${token}`;
    console.log("🔗 Request:", config.baseURL + config.url);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Handling
api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (!error.response) console.error("🌐 Network/CORS Issue:", error.message);
    if (error.response?.status === 401) {
      localStorage.clear();
      window.location.href = "/";
    }
    return Promise.reject(error);
  }
);

export const setAuthToken = (token: string | null) => {
  if (token) api.defaults.headers.Authorization = `Bearer ${token}`;
  else delete api.defaults.headers.Authorization;
};

export const handleLogout = () => {
  localStorage.clear();
  delete api.defaults.headers.Authorization;
};

// -----------------------------------------------------------------------------
// AUTH API
// -----------------------------------------------------------------------------
export const AuthAPI = {
  login: (data: LoginRequest) => api.post<JwtResponse>("/api/v1/auth/login", data),
};

// -----------------------------------------------------------------------------
// USER API
// -----------------------------------------------------------------------------
export const UserAPI = {
  create: (data: CreateUserRequest) => api.post<UserDTO>("/api/v1/users", data),
  get: (id: string) => api.get<UserDTO>(`/api/v1/users/${id}`),
  update: (id: string, data: UpdateUserRequest) => api.put(`/api/v1/users/${id}`, data),
  delete: (id: string) => api.delete(`/api/v1/users/${id}`),
};

// -----------------------------------------------------------------------------
// CONVERSATION API
// -----------------------------------------------------------------------------
export const ConversationAPI = {
  create: (data: CreateConvRequest) => api.post("/api/v1/conversations", data),
  get: (id: string) => api.get(`/api/v1/conversations/${id}`),
  getByUser: (userId: string) => api.get(`/api/v1/conversations/user/${userId}`),
  updateTitle: (id: string, title: string) =>
    api.put(`/api/v1/conversations/${id}/title`, { title }),
  delete: (id: string) => api.delete(`/api/v1/conversations/${id}`),
};

// -----------------------------------------------------------------------------
// MESSAGE API
// -----------------------------------------------------------------------------
export const MessageAPI = {
  create: (data: CreateMessageRequest) => api.post(`/api/v1/messages`, data),
  update: (id: string, content: string) => api.put(`/api/v1/messages/${id}`, { content }),
  delete: (id: string) => api.delete(`/api/v1/messages/${id}`),
};

// -----------------------------------------------------------------------------
// AI API + Streaming SSE
// -----------------------------------------------------------------------------
export const AIApi = {
  analyze: (data: AiRequest) => api.post(`/api/v1/ai/analyze`, data),
  generateResponse: (data: AiRequest) => api.post(`/api/v1/ai/generate-response`, data),

  /** SSE STREAMING FIXED + WORKING */
  streamSearch: async (
    data: AiRequest,
    onEvent: (event: any) => void,
    onComplete?: () => void,
    onError?: (error: any) => void
  ) => {
    try {
      console.log("🚀 Starting Stream ...");

      const response = await fetch(`${API_BASE}/api/v1/ai/stream-search`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
        body: JSON.stringify(data),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader!.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const chunks = buffer.split("\n\n");
        buffer = chunks.pop() || "";

        chunks.forEach((chunk) => {
          const event = parseSSEEvent(chunk);
          if (!event) return;

          if (event.data === "[DONE]") return onComplete?.();
          try {
            onEvent(JSON.parse(event.data));
          } catch {
            onEvent({ text: event.data });
          }
        });
      }

      onComplete?.();
    } catch (e) {
      console.error("❌ Streaming Error:", e);
      onError?.(e);
    }
  },

  /** NEW SSE STREAMING ENDPOINT */
  streamAiResponse: async (
    data: AiRequest,
    onEvent: (event: any) => void,
    onComplete?: () => void,
    onError?: (error: any) => void
  ) => {
    try {
      console.log("🚀 Starting Stream to new endpoint...");

      const response = await fetch(`${API_BASE}/api/v1/ai/stream-ai-response`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
        body: JSON.stringify(data),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader!.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const chunks = buffer.split("\n\n");
        buffer = chunks.pop() || "";

        chunks.forEach((chunk) => {
          const event = parseSSEEvent(chunk);
          if (!event) return;

          if (event.data === "[DONE]") return onComplete?.();
          try {
            onEvent(JSON.parse(event.data));
          } catch {
            onEvent({ text: event.data });
          }
        });
      }

      onComplete?.();
    } catch (e) {
      console.error("❌ Streaming Error:", e);
      onError?.(e);
    }
  },
};

// standalone SSE parser (previously misplaced)
function parseSSEEvent(block: string): { data: string } | null {
  const lines = block.split("\n");
  const dataLines = lines.filter((l) => l.startsWith("data:"));
  if (!dataLines.length) return null;
  return { data: dataLines.map((l) => l.replace("data:", "").trim()).join("\n") };
}