// src/app/api/routes.ts
import axios, { AxiosResponse } from 'axios';

// -----------------------------------------------------------------------------
// Base URL – change once if you move the backend
// -----------------------------------------------------------------------------
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

// -----------------------------------------------------------------------------
// DTOs – mirror the Java records / DTOs on the backend
// -----------------------------------------------------------------------------
export interface UserDTO {
  id: string;               // UUID as string
  username: string;
  email: string;
}

export interface CreateUserRequest {
  username: string;
  email: string;
  password: string;
}

export interface UpdateUserRequest {
  username: string;
  email: string;
  password?: string;        // optional – only sent when changing password
}

export interface ConversationDTO {
  id: string;
  title: string;
  createdAt: string;        // ISO timestamp
  messages: MessageDTO[];
}

export interface CreateConvRequest {
  userId: string;           // UUID
  title: string;
}

export interface MessageDTO {
  id: string;
  role: 'USER' | 'AI';
  content: string;
  sentAt: string;
}

export interface CreateMessageRequest {
  convId: string;
  role: 'USER' | 'AI';
  content: string;
}

// -----------------------------------------------------------------------------
// Helper – generic Axios wrapper (you can add interceptors for JWT later)
// -----------------------------------------------------------------------------
const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

/** Optional: add JWT to every request */
export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

// -----------------------------------------------------------------------------
// USER ENDPOINTS – /api/v1/users
// -----------------------------------------------------------------------------
export const UserAPI = {
  /** POST /api/v1/users */
  create: (data: CreateUserRequest): Promise<AxiosResponse<UserDTO>> =>
    api.post<UserDTO>('/api/v1/users', data),

  /** GET /api/v1/users/{id} */
  get: (id: string): Promise<AxiosResponse<UserDTO>> =>
    api.get<UserDTO>(`/api/v1/users/${id}`),

  /** PUT /api/v1/users/{id} */
  update: (id: string, data: UpdateUserRequest): Promise<AxiosResponse<UserDTO>> =>
    api.put<UserDTO>(`/api/v1/users/${id}`, data),

  /** DELETE /api/v1/users/{id} */
  delete: (id: string): Promise<AxiosResponse<void>> =>
    api.delete<void>(`/api/v1/users/${id}`),
};

// -----------------------------------------------------------------------------
// CONVERSATION ENDPOINTS – /api/v1/conversations
// -----------------------------------------------------------------------------
export const ConversationAPI = {
  /** POST /api/v1/conversations */
  create: (data: CreateConvRequest): Promise<AxiosResponse<ConversationDTO>> =>
    api.post<ConversationDTO>('/api/v1/conversations', data),

  /** GET /api/v1/conversations/{id} */
  get: (id: string): Promise<AxiosResponse<ConversationDTO>> =>
    api.get<ConversationDTO>(`/api/v1/conversations/${id}`),

  /** PUT /api/v1/conversations/{id}/title */
  updateTitle: (
    id: string,
    title: string
  ): Promise<AxiosResponse<ConversationDTO>> =>
    api.put<ConversationDTO>(`/api/v1/conversations/${id}/title`, { title }),

  /** DELETE /api/v1/conversations/{id} */
  delete: (id: string): Promise<AxiosResponse<void>> =>
    api.delete<void>(`/api/v1/conversations/${id}`),
};

// -----------------------------------------------------------------------------
// MESSAGE ENDPOINTS – /api/v1/messages
// -----------------------------------------------------------------------------
export const MessageAPI = {
  /** POST /api/v1/messages */
  create: (data: CreateMessageRequest): Promise<AxiosResponse<MessageDTO>> =>
    api.post<MessageDTO>('/api/v1/messages', data),

  /** PUT /api/v1/messages/{id} */
  update: (
    id: string,
    content: string
  ): Promise<AxiosResponse<MessageDTO>> =>
    api.put<MessageDTO>(`/api/v1/messages/${id}`, { content }),

  /** DELETE /api/v1/messages/{id} */
  delete: (id: string): Promise<AxiosResponse<void>> =>
    api.delete<void>(`/api/v1/messages/${id}`),
};

// -----------------------------------------------------------------------------
// LEGACY ENDPOINTS (if you still expose the old ChatController)
// -----------------------------------------------------------------------------
export const LegacyChatAPI = {
  /** POST /api/chat/conversation */
  startConversation: (
    userId: string,
    title: string
  ): Promise<AxiosResponse<any>> =>
    api.post('/api/chat/conversation', { userId, title }),

  /** POST /api/chat/message */
  sendMessage: (
    convId: string,
    role: 'USER' | 'AI',
    content: string
  ): Promise<AxiosResponse<any>> =>
    api.post('/api/chat/message', { convId, role, content }),
};