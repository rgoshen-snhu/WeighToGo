import { describe, expect, it } from 'vitest';

import { convertWeight } from './unit-conversion';

describe('convertWeight', () => {
  it('converts 1 lb to kilograms using the NIST factor', () => {
    expect(convertWeight(1, 'lbs', 'kg')).toBeCloseTo(0.45359237, 8);
  });

  it('converts 1 kg to pounds (inverse of the NIST factor)', () => {
    expect(convertWeight(1, 'kg', 'lbs')).toBeCloseTo(1 / 0.45359237, 8);
  });

  it('returns the same value when units match (lbs)', () => {
    expect(convertWeight(175.5, 'lbs', 'lbs')).toBe(175.5);
  });

  it('returns the same value when units match (kg)', () => {
    expect(convertWeight(80, 'kg', 'kg')).toBe(80);
  });

  it('round-trips lbs -> kg -> lbs within tolerance', () => {
    const original = 200;
    const back = convertWeight(convertWeight(original, 'lbs', 'kg'), 'kg', 'lbs');
    expect(back).toBeCloseTo(original, 6);
  });

  it('converts 100 lb to about 45.36 kg', () => {
    expect(convertWeight(100, 'lbs', 'kg')).toBeCloseTo(45.359237, 6);
  });

  it('throws on an unrecognised source unit (runtime defence in depth)', () => {
    // Cast past the type system to exercise the explicit default branch.
    expect(() => convertWeight(100, 'stones' as 'lbs', 'kg')).toThrow(/Unknown weight unit/);
  });

  it('throws on an unrecognised target unit rather than mislabelling the result', () => {
    // A valid source with an invalid target must not silently return a
    // converted-but-mislabelled value; cast past the type system to reach it.
    expect(() => convertWeight(100, 'lbs', 'stones' as 'kg')).toThrow(/Unknown weight unit/);
  });
});
