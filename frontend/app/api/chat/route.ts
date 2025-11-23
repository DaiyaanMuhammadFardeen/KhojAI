// src/app/api/routes.ts
import axios, { AxiosResponse } from 'axios';
import { useRouter } from 'next/navigation';

// -----------------------------------------------------------------------------
// Base URL – change once if you move the backend
// -----------------------------------------------------------------------------
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

console.log('API Base URL being used:', API_BASE);

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

export interface AiRequest {
  prompt: string;
}

export interface AiResponse {
  message: string;
}

// -----------------------------------------------------------------------------
// Helper – generic Axios wrapper (you can add interceptors for JWT later)
// -----------------------------------------------------------------------------
const api = axios.create({
  baseURL: API_BASE,
  headers: { 
    'Content-Type': 'application/json',
  },
  withCredentials: true, // This is important for CORS
  timeout: 0, // Remove timeout limit for chatbot
});

// Add a response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle CORS and network errors
    if (!error.response) {
      console.error('Network error or CORS issue:', error.message);
      console.error('Error details:', error.toJSON ? error.toJSON() : error);
      // Show user-friendly error message
      if (error.code === 'NETWORK_ERROR') {
        console.error('Possible CORS issue. Please check your backend configuration.');
      }
    }
    return Promise.reject(error);
  }
);

// Add a request interceptor to log requests
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage and add to headers if it exists
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log('Making request to:', config.baseURL + config.url);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token is invalid or expired, redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('userId');
      localStorage.removeItem('username');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

/** Optional: add JWT to every request */
export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

/** Handle user logout */
export const handleLogout = () => {
  // Clear all user-related data from localStorage
  localStorage.removeItem('token');
  localStorage.removeItem('userId');
  localStorage.removeItem('username');
  localStorage.removeItem('conversations');
  
  // Remove authorization header from API client
  delete api.defaults.headers.common['Authorization'];
};

// -----------------------------------------------------------------------------
// AUTH ENDPOINTS – /api/v1/auth
// -----------------------------------------------------------------------------
export const AuthAPI = {
  /** POST /api/v1/auth/login */
  login: async (data: LoginRequest): Promise<AxiosResponse<JwtResponse>> => {
    try {
      console.log('Sending login request to:', API_BASE + '/api/v1/auth/login');
      const response = await api.post<JwtResponse>('/api/v1/auth/login', data);
      return response;
    } catch (error) {
      console.error('Error in AuthAPI.login:', error);
      throw error;
    }
  },
};

// -----------------------------------------------------------------------------
// USER ENDPOINTS – /api/v1/users
// -----------------------------------------------------------------------------
export const UserAPI = {
  /** POST /api/v1/users */
  create: async (data: CreateUserRequest): Promise<AxiosResponse<UserDTO>> => {
    try {
      console.log('Sending user creation request to:', API_BASE + '/api/v1/users');
      const response = await api.post<UserDTO>('/api/v1/users', data);
      return response;
    } catch (error) {
      console.error('Error in UserAPI.create:', error);
      throw error;
    }
  },

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

  /** GET /api/v1/conversations/user/{userId} */
  getByUser: (userId: string): Promise<AxiosResponse<ConversationDTO[]>> =>
    api.get<ConversationDTO[]>(`/api/v1/conversations/user/${userId}`),

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
  create: (data: CreateMessageRequest): Promise<AxiosResponse<ConversationDTO>> =>
    api.post<ConversationDTO>('/api/v1/messages', data),

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
// AI ENDPOINTS – /api/v1/ai
// -----------------------------------------------------------------------------
export const AIApi = {
  /** POST /api/v1/ai/analyze */
  analyze: (data: AiRequest): Promise<AxiosResponse<AiResponse>> =>
    api.post<AiResponse>('/api/v1/ai/analyze', data),

  /** POST /api/v1/ai/generate-response */
  generateResponse: (data: AiRequest): Promise<AxiosResponse<AiResponse>> =>
    api.post<AiResponse>('/api/v1/ai/generate-response', data),
};