/**
 * Blog service for API communication.
 */

import { apiClient } from './api';

export interface AuthorInfo {
  id: string;
  full_name: string | null;
}

export interface TranslationInfo {
  locale: string;
  slug: string;
  title: string;
}

export interface BlogPost {
  id: string;
  slug: string;
  locale: string;
  translation_key: string | null;
  title: string;
  subtitle: string | null;
  content: string;
  excerpt: string;
  category: string;
  tags: string[];
  featured_image_url: string | null;
  seo_title: string | null;
  seo_description: string | null;
  seo_keywords: string[] | null;
  read_time_minutes: number;
  views_count: number;
  is_featured: boolean;
  published_at: string | null;
  created_at: string;
  updated_at: string;
  author: AuthorInfo | null;
  available_translations: TranslationInfo[] | null;
}

export interface BlogPostListItem {
  id: string;
  slug: string;
  locale: string;
  translation_key: string | null;
  title: string;
  subtitle: string | null;
  excerpt: string;
  category: string;
  tags: string[];
  featured_image_url: string | null;
  read_time_minutes: number;
  views_count: number;
  is_featured: boolean;
  published_at: string | null;
  created_at: string;
  author: AuthorInfo | null;
}

export interface BlogPostListResponse {
  items: BlogPostListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface BlogCategoryCount {
  category: string;
  count: number;
}

export interface BlogTagCount {
  tag: string;
  count: number;
}

export interface BlogMetadata {
  categories: BlogCategoryCount[];
  popular_tags: BlogTagCount[];
  total_posts: number;
}

export interface GetPostsParams {
  page?: number;
  page_size?: number;
  category?: string;
  tag?: string;
  locale?: string;
}

/**
 * Get paginated list of published blog posts.
 */
export async function getBlogPosts(params: GetPostsParams = {}): Promise<BlogPostListResponse> {
  const searchParams = new URLSearchParams();

  if (params.page) searchParams.set('page', params.page.toString());
  if (params.page_size) searchParams.set('page_size', params.page_size.toString());
  if (params.category) searchParams.set('category', params.category);
  if (params.tag) searchParams.set('tag', params.tag);
  if (params.locale) searchParams.set('locale', params.locale);

  const queryString = searchParams.toString();
  const url = queryString ? `/api/v1/blog/posts?${queryString}` : '/api/v1/blog/posts';

  return apiClient.get<BlogPostListResponse>(url);
}

/**
 * Get a single blog post by slug.
 */
export async function getBlogPost(slug: string, locale?: string): Promise<BlogPost> {
  const searchParams = new URLSearchParams();
  if (locale) searchParams.set('locale', locale);
  const queryString = searchParams.toString();
  const url = queryString
    ? `/api/v1/blog/posts/${slug}?${queryString}`
    : `/api/v1/blog/posts/${slug}`;
  return apiClient.get<BlogPost>(url);
}

/**
 * Get blog metadata (categories, tags, total posts).
 */
export async function getBlogMetadata(locale?: string): Promise<BlogMetadata> {
  const searchParams = new URLSearchParams();
  if (locale) searchParams.set('locale', locale);
  const queryString = searchParams.toString();
  const url = queryString ? `/api/v1/blog/metadata?${queryString}` : '/api/v1/blog/metadata';
  return apiClient.get<BlogMetadata>(url);
}

/**
 * Get recent blog posts.
 */
export async function getRecentPosts(
  limit: number = 5,
  locale?: string
): Promise<BlogPostListItem[]> {
  const searchParams = new URLSearchParams();
  searchParams.set('limit', limit.toString());
  if (locale) searchParams.set('locale', locale);
  return apiClient.get<BlogPostListItem[]>(`/api/v1/blog/recent?${searchParams.toString()}`);
}
