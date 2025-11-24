/**
 * RAG (Retrieval-Augmented Generation) API service
 */

import { apiClient } from './api';

export interface RagDocument {
  id: string;
  title: string;
  document_type: string;
  content_preview: string;
  page: number | null;
  source: string | null;
  created_at: string;
  indexed: boolean;
}

export interface RagDocumentListResponse {
  documents: RagDocument[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface RagStats {
  total_documents: number;
  indexed_documents: number;
  documents_by_type: Record<string, number>;
  bm25_stats: Record<string, unknown>;
  qdrant_stats: Record<string, unknown> | null;
}

/**
 * List RAG documents with pagination
 */
export async function listRagDocuments(
  page: number = 1,
  pageSize: number = 20,
  documentType?: string
): Promise<RagDocumentListResponse> {
  let endpoint = `/api/v1/rag/documents?page=${page}&page_size=${pageSize}`;
  if (documentType) {
    endpoint += `&document_type=${documentType}`;
  }
  return apiClient.get<RagDocumentListResponse>(endpoint);
}

/**
 * Get RAG statistics
 */
export async function getRagStats(): Promise<RagStats> {
  return apiClient.get<RagStats>('/api/v1/rag/stats');
}
