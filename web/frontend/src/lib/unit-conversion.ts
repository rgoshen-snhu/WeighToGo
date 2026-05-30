/**
 * Pure weight-unit conversion for display (FR-W-6).
 *
 * Framework-free domain function — mirrors the backend
 * `weighttogo.shared.units.convert_weight`. Display-only: callers convert a
 * stored row value into the user's preferred unit at render time; the stored
 * unit is never mutated.
 *
 * Complexity: O(1) time, O(1) space.
 */

export type WeightUnit = 'lbs' | 'kg';

/**
 * 1 pound expressed in kilograms (exact NIST value). Symbolic constant — no
 * magic number at the call site. Non-zero by construction, so the kg->lbs
 * division below has no zero-divisor risk.
 */
const LBS_TO_KG = 0.45359237;

/**
 * Convert `value` from `fromUnit` to `toUnit`.
 *
 * Weight conversion is purely multiplicative (offset-free, unlike temperature),
 * so the same factor applies to absolute weights and to deltas/rates.
 *
 * @param value    - The weight value to convert.
 * @param fromUnit - The source unit, 'lbs' or 'kg'.
 * @param toUnit   - The target unit, 'lbs' or 'kg'.
 * @returns The converted weight as a number.
 * @throws {Error} When `fromUnit` or `toUnit` is not a recognised unit. The
 *   typed parameters are the primary guard; these branches are defence in depth
 *   at runtime, mirroring the backend `convert_weight` which validates both
 *   units before converting so an unknown target can never be mislabelled.
 */
export function convertWeight(value: number, fromUnit: WeightUnit, toUnit: WeightUnit): number {
  if (fromUnit === toUnit) {
    return value;
  }
  if (fromUnit === 'lbs' && toUnit === 'kg') {
    return value * LBS_TO_KG;
  }
  if (fromUnit === 'kg' && toUnit === 'lbs') {
    return value / LBS_TO_KG;
  }
  // Unreachable for well-typed callers; explicit default keeps the branch total
  // and prevents a valid source with an unknown target returning a mislabelled
  // value. `fromUnit === toUnit` above already handled the matching-unit case.
  const unknown = fromUnit === 'lbs' || fromUnit === 'kg' ? toUnit : fromUnit;
  throw new Error(`Unknown weight unit: ${String(unknown)}`);
}
