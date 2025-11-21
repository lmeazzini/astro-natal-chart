/**
 * TypeScript types for PDF export functionality
 */

export type PDFStatus = 'idle' | 'generating' | 'ready' | 'failed' | 'not_found';

export interface GeneratePDFResponse {
  message: string;
  chart_id: string;
  task_id: string;
}

/**
 * PDF Download Response (matches PDFDownloadResponse schema from API)
 * This is the response from GET /api/v1/charts/{chart_id}/pdf-status
 */
export interface PDFStatusResponse {
  status: PDFStatus; // 'ready', 'generating', 'failed', or 'not_found'
  download_url: string | null; // Presigned S3 URL or local path
  task_id: string | null; // Celery task ID if generating
  expires_in: number | null; // Seconds until download URL expires (for S3)
  generated_at: string | null; // ISO 8601 timestamp
  message: string | null; // Human-readable status message
}

export interface PDFError {
  detail: string;
  status?: number;
}
