/**
 * Test setup file for Vitest
 *
 * Configures the test environment with jsdom and mocks.
 */

import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';

// Initialize i18next for tests with pt-BR as default
import i18n from '@/i18n';

// Force pt-BR language for consistent test results
i18n.changeLanguage('pt-BR');

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock window.matchMedia for components using media queries
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});
