/**
 * React Error Boundary with Amplitude tracking.
 * Catches JavaScript errors anywhere in the child component tree,
 * logs them to Amplitude, and displays a fallback UI.
 */

import { Component, ErrorInfo, ReactNode } from 'react';
import { amplitudeService } from '@/services/amplitude';
import {
  sanitizeErrorMessage,
  sanitizeStackTrace,
  extractComponentName,
} from '@/utils/errorSanitizer';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const componentName = extractComponentName(errorInfo.componentStack);

    // Track error in Amplitude (non-blocking)
    try {
      amplitudeService.track('error_occurred', {
        error_type: 'runtime',
        error_message: sanitizeErrorMessage(error.message),
        page_path: window.location.pathname,
        component_name: componentName,
        stack_trace_snippet: sanitizeStackTrace(error.stack),
        source: 'error_boundary',
      });
    } catch {
      // Silently fail - don't let tracking errors cause more problems
    }

    // Log to console for debugging
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className="min-h-screen flex items-center justify-center bg-background p-4">
          <Card className="max-w-md w-full">
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10">
                <AlertTriangle className="h-6 w-6 text-destructive" />
              </div>
              <CardTitle className="text-xl">Something went wrong</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-center text-muted-foreground">
                We encountered an unexpected error. Please try refreshing the page.
              </p>
              <div className="flex flex-col gap-2 sm:flex-row sm:justify-center">
                <Button onClick={this.handleReload} className="gap-2">
                  <RefreshCw className="h-4 w-4" />
                  Refresh Page
                </Button>
                <Button variant="outline" onClick={this.handleGoHome}>
                  Go to Home
                </Button>
              </div>
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <details className="mt-4 rounded border p-2 text-xs">
                  <summary className="cursor-pointer font-medium">Error Details</summary>
                  <pre className="mt-2 overflow-auto whitespace-pre-wrap text-destructive">
                    {this.state.error.message}
                  </pre>
                </details>
              )}
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}
