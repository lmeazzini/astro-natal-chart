import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import { ErrorBoundary } from './components/ErrorBoundary';
import { amplitudeService } from './services/amplitude';
import { sanitizeErrorMessage, sanitizeStackTrace } from './utils/errorSanitizer';
import './styles/globals.css';
import './i18n'; // Initialize i18n

// Global unhandled error handler
window.addEventListener('error', (event) => {
  try {
    amplitudeService.track('error_occurred', {
      error_type: 'runtime',
      error_message: sanitizeErrorMessage(event.message || 'Unknown error'),
      page_path: window.location.pathname,
      component_name: 'global',
      stack_trace_snippet: sanitizeStackTrace(event.error?.stack),
      source: 'global_handler',
    });
  } catch {
    // Silently fail - don't let tracking errors cause more problems
  }
});

// Global unhandled promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
  try {
    const message =
      event.reason instanceof Error
        ? event.reason.message
        : String(event.reason || 'Unknown rejection');
    amplitudeService.track('error_occurred', {
      error_type: 'runtime',
      error_message: sanitizeErrorMessage(message),
      page_path: window.location.pathname,
      component_name: 'global',
      stack_trace_snippet: sanitizeStackTrace(event.reason?.stack),
      source: 'unhandled_rejection',
    });
  } catch {
    // Silently fail - don't let tracking errors cause more problems
  }
});

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </ErrorBoundary>
  </React.StrictMode>
);
