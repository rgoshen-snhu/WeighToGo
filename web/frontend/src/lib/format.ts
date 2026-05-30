/**
 * Formatting utilities for display values throughout the application.
 *
 * All functions are pure — they take a value and return a string — so they
 * are straightforward to test and use in any context.
 */

import type { Preferences } from '../contexts/PreferencesContext';
import { convertWeight, type WeightUnit } from './unit-conversion';

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
 * Format a stored weight value in the user's preferred unit (FR-W-6).
 *
 * Converts `value` from its stored `storedUnit` into `preferredUnit` for
 * display only, then formats via {@link formatWeight}. The stored value is
 * never mutated; callers pass the row's original unit unchanged.
 *
 * @param value         - The stored weight value.
 * @param storedUnit    - The unit the value was recorded in.
 * @param preferredUnit - The unit the user wants to see.
 *
 * @example
 * formatWeightInPreferredUnit(100, 'lbs', 'kg')  // '45.4 kg'
 */
export function formatWeightInPreferredUnit(
  value: number,
  storedUnit: WeightUnit,
  preferredUnit: WeightUnit,
): string {
  return formatWeight(convertWeight(value, storedUnit, preferredUnit), preferredUnit);
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

/**
 * Format an ISO 8601 observation-date string for display in the weight history.
 *
 * Alias for {@link formatDate} with a domain-specific name that makes call
 * sites in weight-entry components read naturally.
 *
 * @param isoDate - An ISO 8601 date string, e.g. '2026-05-22'.
 */
export function formatObservationDate(isoDate: string): string {
  return formatDate(isoDate);
}
