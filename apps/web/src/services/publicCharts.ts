/**
 * Public Charts API service
 *
 * Provides access to famous people's natal charts without authentication.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface PublicChartPreview {
  id: string;
  slug: string;
  full_name: string;
  category: string | null;
  birth_datetime: string;
  birth_timezone: string;
  city: string | null;
  country: string | null;
  photo_url: string | null;
  short_bio: string | null;
  view_count: number;
  featured: boolean;
  created_at: string;
}

export interface PublicChartDetail extends PublicChartPreview {
  latitude: number;
  longitude: number;
  chart_data: Record<string, unknown> | null;
  house_system: string;
  highlights: string[] | null;
  meta_title: string | null;
  meta_description: string | null;
  meta_keywords: string[] | null;
  is_published: boolean;
  updated_at: string;
}

export interface PublicChartList {
  charts: PublicChartPreview[];
  total: number;
  page: number;
  page_size: number;
}

export interface CategoryCount {
  category: string;
  count: number;
}

export interface ListPublicChartsParams {
  category?: string;
  search?: string;
  sort?: 'name' | 'date' | 'views';
  page?: number;
  page_size?: number;
}

/**
 * List public charts with optional filters
 */
export async function listPublicCharts(
  params: ListPublicChartsParams = {}
): Promise<PublicChartList> {
  const searchParams = new URLSearchParams();

  if (params.category) searchParams.set('category', params.category);
  if (params.search) searchParams.set('search', params.search);
  if (params.sort) searchParams.set('sort', params.sort);
  if (params.page) searchParams.set('page', params.page.toString());
  if (params.page_size) searchParams.set('page_size', params.page_size.toString());

  const queryString = searchParams.toString();
  const url = `${API_BASE_URL}/api/v1/public-charts${queryString ? `?${queryString}` : ''}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error('Failed to fetch public charts');
  }

  return response.json();
}

/**
 * Get a public chart by slug
 */
export async function getPublicChart(slug: string): Promise<PublicChartDetail> {
  const response = await fetch(`${API_BASE_URL}/api/v1/public-charts/${slug}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Public chart not found');
    }
    throw new Error('Failed to fetch public chart');
  }

  return response.json();
}

/**
 * Get featured public charts
 */
export async function getFeaturedCharts(limit: number = 10): Promise<PublicChartPreview[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/public-charts/featured?limit=${limit}`
  );

  if (!response.ok) {
    throw new Error('Failed to fetch featured charts');
  }

  return response.json();
}

/**
 * Get all categories with chart counts
 */
export async function getCategories(): Promise<CategoryCount[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/public-charts/categories`);

  if (!response.ok) {
    throw new Error('Failed to fetch categories');
  }

  return response.json();
}

/**
 * Category labels for display
 */
export const CATEGORY_LABELS: Record<string, string> = {
  scientist: 'Cientistas',
  artist: 'Artistas',
  leader: 'Líderes',
  writer: 'Escritores',
  athlete: 'Atletas',
  actor: 'Atores',
  musician: 'Músicos',
  entrepreneur: 'Empreendedores',
  historical: 'Figuras Históricas',
  other: 'Outros',
};

/**
 * Get translated category label
 */
export function getCategoryLabel(category: string): string {
  return CATEGORY_LABELS[category] || category;
}
