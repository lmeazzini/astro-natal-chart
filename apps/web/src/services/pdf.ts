/**
 * PDF export service for generating and downloading natal chart PDFs
 */

import { apiClient } from './api';
import type { GeneratePDFResponse, PDFStatusResponse } from '@/types/pdf';

/**
 * Trigger PDF generation for a birth chart (async)
 *
 * This starts a background task to generate the PDF. Poll getPDFStatus()
 * to check when it's ready.
 *
 * @param chartId - Birth chart UUID
 * @param token - JWT authentication token
 * @returns Generation task information
 */
export async function generateChartPDF(
  chartId: string,
  token: string
): Promise<GeneratePDFResponse> {
  return apiClient.post<GeneratePDFResponse>(
    `/api/v1/charts/${chartId}/generate-pdf`,
    undefined,
    token
  );
}

/**
 * Check PDF generation status
 *
 * Poll this endpoint after calling generateChartPDF() to check if the PDF
 * is ready. When pdf_status === 'completed', you can download the PDF.
 *
 * @param chartId - Birth chart UUID
 * @param token - JWT authentication token
 * @returns PDF status information
 */
export async function getPDFStatus(
  chartId: string,
  token: string
): Promise<PDFStatusResponse> {
  return apiClient.get<PDFStatusResponse>(
    `/api/v1/charts/${chartId}/pdf-status`,
    token
  );
}

/**
 * Download generated PDF
 *
 * Downloads the PDF file. Only call this after getPDFStatus() returns
 * pdf_status === 'completed'.
 *
 * This function triggers a browser download by creating a temporary link.
 *
 * @param chartId - Birth chart UUID
 * @param token - JWT authentication token
 * @param personName - Person's name for the filename (optional)
 */
export async function downloadChartPDF(
  chartId: string,
  token: string,
  personName?: string
): Promise<void> {
  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const url = `${API_BASE_URL}/api/v1/charts/${chartId}/download-pdf`;

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to download PDF');
    }

    // Get filename from Content-Disposition header or construct default
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = `natal_chart_${chartId}.pdf`;

    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    } else if (personName) {
      filename = `natal_chart_${personName}_${chartId}.pdf`.replace(/\s+/g, '_');
    }

    // Create blob and download
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Unknown error downloading PDF');
  }
}

/**
 * Helper function: Generate PDF and poll until ready, then download
 *
 * This is a convenience function that combines all three steps:
 * 1. Generate PDF
 * 2. Poll status every 2 seconds until ready
 * 3. Auto-download when complete
 *
 * @param chartId - Birth chart UUID
 * @param token - JWT authentication token
 * @param personName - Person's name for the filename
 * @param onProgress - Optional callback for progress updates
 * @returns Promise that resolves when PDF is downloaded
 */
export async function generateAndDownloadPDF(
  chartId: string,
  token: string,
  personName?: string,
  onProgress?: (status: PDFStatusResponse) => void
): Promise<void> {
  // Step 1: Trigger generation
  await generateChartPDF(chartId, token);

  // Step 2: Poll until ready
  const pollInterval = 2000; // 2 seconds
  const maxAttempts = 150; // 5 minutes max (150 * 2s = 300s)
  let attempts = 0;

  while (attempts < maxAttempts) {
    await new Promise((resolve) => setTimeout(resolve, pollInterval));

    const status = await getPDFStatus(chartId, token);
    onProgress?.(status);

    if (status.status === 'ready') {
      // Step 3: Download
      await downloadChartPDF(chartId, token, personName);
      return;
    }

    if (status.status === 'failed') {
      throw new Error(status.message || 'PDF generation failed');
    }

    attempts++;
  }

  throw new Error('PDF generation timeout - exceeded 5 minutes');
}
