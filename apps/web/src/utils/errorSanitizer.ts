/**
 * Error sanitization utilities for Amplitude tracking.
 * Removes PII (Personally Identifiable Information) from error messages
 * to ensure privacy compliance.
 */

/**
 * Sanitizes an error message by removing sensitive information.
 * - Emails are replaced with [EMAIL]
 * - Bearer tokens are replaced with Bearer [TOKEN]
 * - Passwords are replaced with password=[REDACTED]
 * - UUIDs are replaced with [UUID]
 */
export function sanitizeErrorMessage(message: string): string {
  if (!message) return '';

  let sanitized = message;

  // Remove emails
  sanitized = sanitized.replace(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g, '[EMAIL]');

  // Remove Bearer tokens
  sanitized = sanitized.replace(/Bearer\s+[A-Za-z0-9-._~+/]+=*/g, 'Bearer [TOKEN]');

  // Remove potential passwords in various formats
  sanitized = sanitized.replace(/password[=:]\s*[^\s&"']+/gi, 'password=[REDACTED]');

  // Remove JWT tokens (three base64 segments separated by dots)
  sanitized = sanitized.replace(
    /eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+/g,
    '[JWT_TOKEN]'
  );

  // Remove UUIDs (potential user IDs, chart IDs, etc.)
  sanitized = sanitized.replace(
    /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi,
    '[UUID]'
  );

  // Remove API keys (common patterns)
  sanitized = sanitized.replace(/sk-[A-Za-z0-9-_]{20,}/g, '[API_KEY]');
  sanitized = sanitized.replace(/api[_-]?key[=:]\s*[^\s&"']+/gi, 'api_key=[REDACTED]');

  return sanitized;
}

/**
 * Sanitizes a stack trace by:
 * 1. Removing PII using sanitizeErrorMessage
 * 2. Truncating to maxLength characters
 */
export function sanitizeStackTrace(stack: string | undefined, maxLength = 200): string {
  if (!stack) return '';
  const truncated = stack.substring(0, maxLength);
  return sanitizeErrorMessage(truncated);
}

/**
 * Extracts a clean component name from React's componentStack.
 * Returns the first meaningful component name, truncated to 100 chars.
 */
export function extractComponentName(componentStack: string | null | undefined): string {
  if (!componentStack) return 'unknown';

  // Component stack looks like:
  // "\n    at ComponentName (file.tsx:123:45)"
  // "\n    at ParentComponent"
  const lines = componentStack.split('\n').filter((line) => line.trim());
  if (lines.length === 0) return 'unknown';

  // Extract the first component name
  const match = lines[0].match(/at\s+([A-Za-z0-9_]+)/);
  if (match && match[1]) {
    return match[1].substring(0, 100);
  }

  return 'unknown';
}
