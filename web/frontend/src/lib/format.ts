/**
 * Formatting utilities for display values throughout the application.
 *
 * All functions are pure — they take a value and return a string — so they
 * are straightforward to test and use in any context.
 */

import type { Preferences } from '../contexts/PreferencesContext';

/**
 * Format a numeric weight value with one decimal place and its unit suffix.
 *
 * @param value - The weight as a number.
 * @param unit  - The display unit ('kg' or 'lbs').
 *
 * @example
 * formatWeight(70, 'kg')      // '70.0 kg'
 * formatWeight(154.4, 'lbs')  // '154.4 lbs'
 */
export function formatWeight(value: number, unit: Preferences['weightUnit']): string {
  return `${value.toFixed(1)} ${unit}`;
}

/**
 * Format an ISO 8601 date string (YYYY-MM-DD) as a human-readable date.
 *
 * Uses the user's locale via `Intl.DateTimeFormat` so the output respects
 * regional conventions. The date is parsed in UTC to avoid timezone offsets
 * shifting the displayed day.
 *
 * @param isoDate - An ISO 8601 date string, e.g. '2026-05-22'.
 *
 * @example
 * formatDate('2026-05-22')  // 'May 22, 2026' (en-US locale)
 */
export function formatDate(isoDate: string): string {
  // Appending 'T00:00:00Z' ensures the date is parsed as UTC, preventing
  // timezone offsets from rolling the display date backwards by one day.
  const date = new Date(`${isoDate}T00:00:00Z`);
  return new Intl.DateTimeFormat(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    timeZone: 'UTC',
  }).format(date);
}
