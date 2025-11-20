/**
 * TypeScript types for PDF export functionality
 */

export type PDFStatus = 'idle' | 'processing' | 'completed' | 'failed';

export interface GeneratePDFResponse {
  message: string;
  chart_id: string;
  task_id: string;
}

export interface PDFStatusResponse {
  chart_id: string;
  pdf_status: PDFStatus;
  pdf_url: string | null;
  pdf_generated_at: string | null;
  error_message: string | null;
}

export interface PDFError {
  detail: string;
  status?: number;
}
