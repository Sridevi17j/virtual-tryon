export interface TryOnRequest {
  personImageUrl?: string;
  garmentImageUrl?: string;
  asyncProcessing?: boolean;
}

export interface TryOnResponse {
  jobId: string;
  status: JobStatus;
  resultUrl?: string;
  message: string;
  createdAt?: string;
  completedAt?: string;
}

export interface JobInfo {
  jobId: string;
  status: JobStatus;
  resultUrl?: string;
  error?: string;
  createdAt: string;
  updatedAt: string;
  personImageUrl?: string;
  garmentImageUrl?: string;
}

export enum JobStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export interface FileUploadResponse {
  fileId: string;
  filename: string;
  fileUrl: string;
  fileSize: number;
  contentType: string;
  uploadedAt: string;
}

export interface UploadedImage {
  id: string;
  file: File;
  preview: string;
  uploadResponse?: FileUploadResponse;
  uploading?: boolean;
  error?: string;
}

export interface HealthResponse {
  status: string;
  services: Record<string, unknown>;
  timestamp: string;
}

export interface ApiError {
  detail: string;
  errorCode?: string;
  timestamp: string;
}

export interface ProcessingStep {
  id: string;
  name: string;
  status: 'waiting' | 'processing' | 'completed' | 'error';
  message?: string;
}

export interface ComparisonImages {
  original: string;
  result: string;
  person: string;
  garment: string;
}