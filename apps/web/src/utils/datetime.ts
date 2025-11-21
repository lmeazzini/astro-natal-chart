/**
 * DateTime utilities for timezone-aware formatting
 *
 * Provides consistent date/time formatting across the application:
 * - System timestamps (created_at, updated_at) in user's local timezone
 * - Birth datetimes preserved in original timezone
 * - Relative time formatting (e.g., "há 2 horas")
 * - Locale-aware formatting based on i18n language setting
 */

import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import relativeTime from 'dayjs/plugin/relativeTime';
import localizedFormat from 'dayjs/plugin/localizedFormat';
import 'dayjs/locale/pt-br';
import 'dayjs/locale/en';
import i18n from '../i18n';

// Configure dayjs plugins
dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.extend(relativeTime);
dayjs.extend(localizedFormat);

/**
 * Get current locale from i18n settings
 * Maps i18n locale to dayjs locale
 */
function getDayjsLocale(): string {
  const lang = i18n.language;
  if (lang?.startsWith('pt')) {
    return 'pt-br';
  }
  return 'en';
}

/**
 * Set dayjs locale based on current i18n language
 */
export function updateDayjsLocale(): void {
  dayjs.locale(getDayjsLocale());
}

// Initialize locale
updateDayjsLocale();

// Listen for i18n language changes
i18n.on('languageChanged', updateDayjsLocale);

/**
 * Get user's timezone from browser
 *
 * @returns {string} IANA timezone name (e.g., "America/Sao_Paulo")
 */
export function getUserTimezone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

/**
 * Get locale-specific date format
 */
function getDateFormat(includeTime: boolean): string {
  const locale = getDayjsLocale();
  if (locale === 'pt-br') {
    return includeTime ? 'DD/MM/YYYY HH:mm' : 'DD/MM/YYYY';
  }
  return includeTime ? 'MM/DD/YYYY h:mm A' : 'MM/DD/YYYY';
}

/**
 * Format system timestamp (created_at, updated_at) to local timezone
 *
 * Converts UTC timestamp to user's local timezone with absolute formatting.
 * Uses locale-aware date format (DD/MM/YYYY for pt-BR, MM/DD/YYYY for en-US).
 *
 * @param {string} isoString - ISO 8601 datetime string in UTC
 * @param {boolean} includeTime - Whether to include time (default: true)
 * @returns {string} Formatted date (e.g., "15/03/2025 14:30" or "03/15/2025 2:30 PM")
 *
 * @example
 * // pt-BR locale:
 * formatLocalDateTime("2025-03-15T17:30:00Z")
 * // => "15/03/2025 14:30" (if user is in America/Sao_Paulo, UTC-3)
 *
 * // en-US locale:
 * formatLocalDateTime("2025-03-15T17:30:00Z")
 * // => "03/15/2025 2:30 PM"
 */
export function formatLocalDateTime(
  isoString: string,
  includeTime = true
): string {
  const userTz = getUserTimezone();
  const format = getDateFormat(includeTime);
  return dayjs(isoString).tz(userTz).format(format);
}

/**
 * Format timestamp as relative time ("há X minutos/horas/dias")
 *
 * For recent timestamps (< 7 days), show relative time.
 * For older timestamps, show absolute date.
 *
 * @param {string} isoString - ISO 8601 datetime string in UTC
 * @param {number} maxDays - Maximum days for relative format (default: 7)
 * @returns {string} Formatted time (e.g., "há 2 horas" or "15/03/2025")
 *
 * @example
 * formatRelativeTime("2025-01-20T15:00:00Z")  // 2 hours ago
 * // => "há 2 horas"
 *
 * formatRelativeTime("2025-01-10T15:00:00Z")  // 10 days ago
 * // => "10/01/2025"
 */
export function formatRelativeTime(
  isoString: string,
  maxDays = 7
): string {
  const date = dayjs(isoString);
  const now = dayjs();
  const daysDiff = now.diff(date, 'days');

  // Use relative time for recent dates
  if (daysDiff < maxDays) {
    return date.fromNow();
  }

  // Use absolute date for older dates
  return formatLocalDateTime(isoString, false);
}

/**
 * Format birth datetime preserving original timezone
 *
 * Birth times should NOT be converted to user's timezone.
 * They represent a specific moment in a specific location.
 * Uses locale-aware date format.
 *
 * @param {string} isoString - ISO 8601 datetime string (with timezone)
 * @param {string} birthTimezone - Original birth timezone (IANA name)
 * @param {boolean} includeTimezone - Show timezone suffix (default: true)
 * @returns {string} Formatted birth datetime
 *
 * @example
 * // pt-BR locale:
 * formatBirthDateTime("1990-03-15T14:30:00-03:00", "America/Sao_Paulo")
 * // => "15/03/1990 14:30 (America/Sao_Paulo)"
 *
 * // en-US locale:
 * formatBirthDateTime("1990-03-15T14:30:00-03:00", "America/Sao_Paulo")
 * // => "03/15/1990 2:30 PM (America/Sao_Paulo)"
 */
export function formatBirthDateTime(
  isoString: string,
  birthTimezone: string,
  includeTimezone = true
): string {
  const format = getDateFormat(true);
  const formatted = dayjs(isoString).tz(birthTimezone).format(format);

  if (includeTimezone) {
    return `${formatted} (${birthTimezone})`;
  }

  return formatted;
}

/**
 * Format date for form input (YYYY-MM-DD)
 *
 * Used in date inputs to set initial values.
 *
 * @param {string} isoString - ISO 8601 datetime string
 * @returns {string} Date in YYYY-MM-DD format
 *
 * @example
 * formatDateForInput("1990-03-15T14:30:00-03:00")
 * // => "1990-03-15"
 */
export function formatDateForInput(isoString: string): string {
  return dayjs(isoString).format('YYYY-MM-DD');
}

/**
 * Format time for form input (HH:mm)
 *
 * Used in time inputs to set initial values.
 *
 * @param {string} isoString - ISO 8601 datetime string
 * @param {string} birthTimezone - Original birth timezone
 * @returns {string} Time in HH:mm format
 *
 * @example
 * formatTimeForInput("1990-03-15T14:30:00-03:00", "America/Sao_Paulo")
 * // => "14:30"
 */
export function formatTimeForInput(
  isoString: string,
  birthTimezone: string
): string {
  return dayjs(isoString).tz(birthTimezone).format('HH:mm');
}

/**
 * Parse date and time into ISO string with timezone
 *
 * Combines date, time, and timezone into an ISO 8601 string.
 *
 * @param {string} date - Date string (YYYY-MM-DD)
 * @param {string} time - Time string (HH:mm)
 * @param {string} timezone - IANA timezone name
 * @returns {string} ISO 8601 datetime string
 *
 * @example
 * parseDateTime("1990-03-15", "14:30", "America/Sao_Paulo")
 * // => "1990-03-15T14:30:00-03:00"
 */
export function parseDateTime(
  date: string,
  time: string,
  timezone: string
): string {
  const dateTime = `${date} ${time}`;
  return dayjs.tz(dateTime, 'YYYY-MM-DD HH:mm', timezone).toISOString();
}

/**
 * Format duration in milliseconds to human-readable string
 *
 * Used for displaying calculation times, PDF generation times, etc.
 *
 * @param {number} ms - Duration in milliseconds
 * @returns {string} Formatted duration (e.g., "2.5s", "1.2m", "3h")
 *
 * @example
 * formatDuration(2500)   // => "2.5s"
 * formatDuration(75000)  // => "1.2m"
 * formatDuration(10800000) // => "3h"
 */
export function formatDuration(ms: number): string {
  if (ms < 1000) {
    return `${ms}ms`;
  } else if (ms < 60000) {
    return `${(ms / 1000).toFixed(1)}s`;
  } else if (ms < 3600000) {
    return `${(ms / 60000).toFixed(1)}m`;
  } else {
    return `${(ms / 3600000).toFixed(1)}h`;
  }
}

/**
 * Check if date is today
 *
 * @param {string} isoString - ISO 8601 datetime string
 * @returns {boolean} True if date is today
 *
 * @example
 * isToday("2025-01-20T15:00:00Z")  // If today is 2025-01-20
 * // => true
 */
export function isToday(isoString: string): boolean {
  return dayjs(isoString).isSame(dayjs(), 'day');
}

/**
 * Check if date is yesterday
 *
 * @param {string} isoString - ISO 8601 datetime string
 * @returns {boolean} True if date is yesterday
 *
 * @example
 * isYesterday("2025-01-19T15:00:00Z")  // If today is 2025-01-20
 * // => true
 */
export function isYesterday(isoString: string): boolean {
  return dayjs(isoString).isSame(dayjs().subtract(1, 'day'), 'day');
}

/**
 * Get short timezone abbreviation
 *
 * Converts IANA timezone to short abbreviation (e.g., BRT, EST).
 *
 * @param {string} timezone - IANA timezone name
 * @returns {string} Short timezone abbreviation
 *
 * @example
 * getTimezoneAbbr("America/Sao_Paulo")
 * // => "BRT" (Brasilia Time)
 *
 * getTimezoneAbbr("America/New_York")
 * // => "EST" or "EDT" (depends on DST)
 */
export function getTimezoneAbbr(timezone: string): string {
  const now = new Date();
  const formatter = new Intl.DateTimeFormat('en-US', {
    timeZone: timezone,
    timeZoneName: 'short',
  });
  const parts = formatter.formatToParts(now);
  const tzPart = parts.find((part) => part.type === 'timeZoneName');
  return tzPart?.value || timezone;
}

// =============================================================================
// Number Formatting Utilities
// =============================================================================

/**
 * Get current locale code for Intl APIs
 */
function getIntlLocale(): string {
  const lang = i18n.language;
  if (lang?.startsWith('pt')) {
    return 'pt-BR';
  }
  return 'en-US';
}

/**
 * Format a number according to current locale
 *
 * @param {number} value - Number to format
 * @param {number} decimals - Number of decimal places (default: 2)
 * @returns {string} Formatted number (e.g., "1.234,56" for pt-BR, "1,234.56" for en-US)
 *
 * @example
 * // pt-BR locale:
 * formatNumber(1234.56) // => "1.234,56"
 *
 * // en-US locale:
 * formatNumber(1234.56) // => "1,234.56"
 */
export function formatNumber(value: number, decimals = 2): string {
  return new Intl.NumberFormat(getIntlLocale(), {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

/**
 * Format a currency value according to current locale
 *
 * @param {number} value - Amount to format
 * @param {string} currency - Currency code (default: BRL for pt-BR, USD for en-US)
 * @returns {string} Formatted currency (e.g., "R$ 1.234,56" for pt-BR, "$1,234.56" for en-US)
 *
 * @example
 * // pt-BR locale:
 * formatCurrency(1234.56) // => "R$ 1.234,56"
 *
 * // en-US locale:
 * formatCurrency(1234.56) // => "$1,234.56"
 */
export function formatCurrency(
  value: number,
  currency?: string
): string {
  const locale = getIntlLocale();
  const currencyCode = currency || (locale === 'pt-BR' ? 'BRL' : 'USD');

  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currencyCode,
  }).format(value);
}

/**
 * Format a percentage value
 *
 * @param {number} value - Value between 0 and 1 (e.g., 0.85 for 85%)
 * @param {number} decimals - Number of decimal places (default: 1)
 * @returns {string} Formatted percentage (e.g., "85,0%" for pt-BR, "85.0%" for en-US)
 *
 * @example
 * // pt-BR locale:
 * formatPercentage(0.856) // => "85,6%"
 *
 * // en-US locale:
 * formatPercentage(0.856) // => "85.6%"
 */
export function formatPercentage(value: number, decimals = 1): string {
  return new Intl.NumberFormat(getIntlLocale(), {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

/**
 * Format a degree value (for astrological positions)
 *
 * @param {number} value - Degree value
 * @param {number} decimals - Number of decimal places (default: 1)
 * @returns {string} Formatted degree (e.g., "15,3°" for pt-BR, "15.3°" for en-US)
 *
 * @example
 * // pt-BR locale:
 * formatDegree(15.345) // => "15,3°"
 *
 * // en-US locale:
 * formatDegree(15.345) // => "15.3°"
 */
export function formatDegree(value: number, decimals = 1): string {
  const formatted = formatNumber(value, decimals);
  return `${formatted}°`;
}
