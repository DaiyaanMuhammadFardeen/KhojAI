// src/app/api/documents/route.ts
import axios, { AxiosResponse } from 'axios';

// -----------------------------------------------------------------------------
// Base URL – change once if you move the backend
// -----------------------------------------------------------------------------
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

// -----------------------------------------------------------------------------
// Helper – generic Axios wrapper (you can add interceptors for JWT later)
// -----------------------------------------------------------------------------
const api = axios.create({
  baseURL: API_BASE,
  headers: { 
    'Content-Type': 'application/json',
  },
  withCredentials: true, // This is important for CORS
});

// Add a request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage and add to headers if it exists
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// -----------------------------------------------------------------------------
// DOCUMENT DTOs
// -----------------------------------------------------------------------------
export interface DocumentDTO {
  id: string;
  name: string;
  type: string;
  size: number;
  uploadedAt: string; // ISO timestamp
  url?: string;
}

export interface UploadDocumentRequest {
  userId: string;
  file: File;
}

// -----------------------------------------------------------------------------
// DOCUMENT ENDPOINTS
// -----------------------------------------------------------------------------
export const DocumentAPI = {
  /**
   * GET /api/v1/documents/user/{userId}
   * Get all documents for a user
   */
  getByUser: (userId: string): Promise<AxiosResponse<DocumentDTO[]>> =>
    api.get<DocumentDTO[]>(`/api/v1/documents/user/${userId}`),

  /**
   * POST /api/v1/documents/upload
   * Upload a document
   */
  upload: async (userId: string, file: File): Promise<AxiosResponse<DocumentDTO>> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('userId', userId);
    
    return api.post<DocumentDTO>('/api/v1/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  /**
   * DELETE /api/v1/documents/{id}
   * Delete a document
   */
  delete: (id: string): Promise<AxiosResponse<void>> =>
    api.delete<void>(`/api/v1/documents/${id}`),
};