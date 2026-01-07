/**
 * Test data factories for E2E tests.
 *
 * These provide consistent test data across all E2E tests.
 */

export const TEST_USER = {
  email: process.env.E2E_TEST_USER_EMAIL || 'e2e-test@example.com',
  password: process.env.E2E_TEST_USER_PASSWORD || 'Test123!@#',
  name: 'E2E Test User',
};

export const INVALID_USER = {
  email: 'invalid@nonexistent.com',
  password: 'WrongPassword123!',
};

/**
 * Generate a unique email for registration tests
 */
export function generateTestEmail(): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 8);
  return `e2e-test-${timestamp}-${random}@example.com`;
}

/**
 * Generate a valid password for registration tests
 */
export function generateTestPassword(): string {
  return 'Test123!@#Secure';
}

/**
 * Test chart data for creating new charts
 */
export const TEST_CHART = {
  personName: 'Test Person',
  birthDate: '1990-06-15',
  birthTime: '14:30',
  birthPlace: 'New York, NY, USA',
  // Pre-geocoded coordinates (used when mocking)
  latitude: 40.7128,
  longitude: -74.006,
  timezone: 'America/New_York',
};

/**
 * Generate unique chart data
 */
export function generateChartData() {
  const timestamp = Date.now();
  return {
    ...TEST_CHART,
    personName: `Test Person ${timestamp}`,
  };
}

/**
 * API endpoints for direct API calls in tests
 */
export const API_ENDPOINTS = {
  login: '/api/v1/auth/login',
  register: '/api/v1/auth/register',
  me: '/api/v1/users/me',
  charts: '/api/v1/charts',
  passwordReset: '/api/v1/auth/forgot-password',
};

/**
 * Local storage keys used by the application
 */
export const STORAGE_KEYS = {
  accessToken: 'astro_access_token',
  refreshToken: 'astro_refresh_token',
};

/**
 * Common page routes
 */
export const ROUTES = {
  home: '/',
  login: '/login',
  register: '/register',
  forgotPassword: '/forgot-password',
  dashboard: '/dashboard',
  newChart: '/charts/new',
  pricing: '/pricing',
  settings: '/settings',
  profile: '/profile',
};
