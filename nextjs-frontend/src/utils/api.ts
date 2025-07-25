import axios, { AxiosResponse } from 'axios';
import { 
  TryOnResponse, 
  FileUploadResponse, 
  JobInfo, 
  HealthResponse 
} from '../types';

// Original local API configuration
// const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

// Updated for Railway backend deployment (commented out - using proxy instead)
// const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://backend-api-production-8f2f.up.railway.app/api/v1';

// Use Netlify proxy to avoid CORS/CSP issues
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for long-running requests
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const apiClient = {
  // Health endpoints - using Netlify proxy
  async getHealth(): Promise<HealthResponse> {
    // Original API client call (commented out)
    // const response: AxiosResponse<HealthResponse> = await api.get('/health');
    
    // Direct fetch to Railway backend (commented out - using proxy instead)
    // const response = await fetch('https://backend-api-production-8f2f.up.railway.app/health');
    
    // Use Netlify proxy for health endpoint
    const response = await fetch('/health');
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }
    return await response.json();
  },

  // File upload endpoints
  async uploadFile(file: File): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response: AxiosResponse<FileUploadResponse> = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  async uploadMultipleFiles(files: File[]): Promise<FileUploadResponse[]> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    const response: AxiosResponse<FileUploadResponse[]> = await api.post('/upload/multiple', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  async deleteFile(fileId: string): Promise<void> {
    await api.delete(`/upload/${fileId}`);
  },

  // Virtual try-on endpoints
  async virtualTryOn(personImage: File, garmentImage: File, asyncProcessing = false): Promise<TryOnResponse> {
    const formData = new FormData();
    formData.append('person_image', personImage);
    formData.append('garment_image', garmentImage);
    formData.append('async_processing', String(asyncProcessing));

    const response: AxiosResponse<TryOnResponse> = await api.post('/tryon', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  async preprocessImage(image: File, imageType: 'person' | 'garment'): Promise<Blob> {
    const formData = new FormData();
    formData.append('image', image);
    formData.append('image_type', imageType);

    const response: AxiosResponse<Blob> = await api.post('/tryon/preprocess', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      responseType: 'blob',
    });

    return response.data;
  },

  async getTryOnResult(jobId: string): Promise<Blob> {
    const response: AxiosResponse<Blob> = await api.get(`/tryon/${jobId}/result`, {
      responseType: 'blob',
    });

    return response.data;
  },

  async getExamples(): Promise<{
    personExamples: string[];
    garmentExamples: string[];
  }> {
    const response = await api.get('/tryon/examples');
    return response.data;
  },

  // Job management endpoints
  async getJobStatus(jobId: string): Promise<JobInfo> {
    const response: AxiosResponse<JobInfo> = await api.get(`/jobs/${jobId}`);
    return response.data;
  },

  async listJobs(status?: string, limit = 100): Promise<JobInfo[]> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    params.append('limit', String(limit));

    const response: AxiosResponse<JobInfo[]> = await api.get(`/jobs?${params.toString()}`);
    return response.data;
  },

  async cancelJob(jobId: string): Promise<void> {
    await api.post(`/jobs/${jobId}/cancel`);
  },

  async deleteJob(jobId: string): Promise<void> {
    await api.delete(`/jobs/${jobId}`);
  },

  async getJobStats(): Promise<{
    total: number;
    pending: number;
    processing: number;
    completed: number;
    failed: number;
    successRate: number;
  }> {
    const response = await api.get('/jobs/stats/summary');
    return response.data;
  },
};

export default apiClient;