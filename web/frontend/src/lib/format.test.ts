import { describe, expect, it } from 'vitest';

import { formatDate, formatWeight } from './format';

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
