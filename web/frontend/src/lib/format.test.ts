import { describe, expect, it } from 'vitest';

import {
  formatDate,
  formatObservationDate,
  formatWeight,
  formatWeightInPreferredUnit,
} from './format';

describe('formatWeight', () => {
  it('formats a weight in kg with one decimal place', () => {
    expect(formatWeight(70, 'kg')).toBe('70.0 kg');
  });

  it('formats a weight in lbs with one decimal place', () => {
    expect(formatWeight(154.4, 'lbs')).toBe('154.4 lbs');
  });

  it('rounds to one decimal place', () => {
    // 70.56 rounds up to 70.6 in standard IEEE 754 toFixed(1) rounding.
    expect(formatWeight(70.56, 'kg')).toBe('70.6 kg');
  });

  it('handles zero weight', () => {
    expect(formatWeight(0, 'kg')).toBe('0.0 kg');
  });
});

describe('formatWeightInPreferredUnit', () => {
  it('converts a stored lbs value to the preferred kg unit for display', () => {
    // 100 lb -> 45.359237 kg -> rounds to 45.4 kg
    expect(formatWeightInPreferredUnit(100, 'lbs', 'kg')).toBe('45.4 kg');
  });

  it('leaves the value unchanged when stored unit equals preferred unit', () => {
    expect(formatWeightInPreferredUnit(154.4, 'lbs', 'lbs')).toBe('154.4 lbs');
  });

  it('converts a stored kg value to the preferred lbs unit for display', () => {
    // 80 kg -> 176.37 lb -> rounds to 176.4 lbs
    expect(formatWeightInPreferredUnit(80, 'kg', 'lbs')).toBe('176.4 lbs');
  });
});

describe('formatDate', () => {
  it('returns a non-empty readable string for a valid ISO date', () => {
    const result = formatDate('2026-05-22');
    expect(typeof result).toBe('string');
    expect(result.length).toBeGreaterThan(0);
    // Should contain some recognisable part of the date — not just an ISO string.
    expect(result).not.toBe('2026-05-22');
  });

  it('includes the year in the formatted output', () => {
    const result = formatDate('2026-05-22');
    expect(result).toContain('2026');
  });
});

describe('formatObservationDate', () => {
  it('returns the same value as formatDate for the same input', () => {
    expect(formatObservationDate('2026-05-22')).toBe(formatDate('2026-05-22'));
  });

  it('includes the year in the formatted output', () => {
    expect(formatObservationDate('2026-05-20')).toContain('2026');
  });
});
