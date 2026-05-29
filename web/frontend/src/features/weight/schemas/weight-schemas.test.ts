import { describe, expect, it } from 'vitest';

import { weightEntrySchema } from './weight-schemas';

const localDate = (d = new Date()) => {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
};
const TODAY = localDate();
const TOMORROW = localDate(new Date(Date.now() + 86_400_000));
const YESTERDAY = localDate(new Date(Date.now() - 86_400_000));

function valid(overrides: Record<string, unknown> = {}) {
  return {
    weight_value: 175.5,
    weight_unit: 'lbs',
    observation_date: TODAY,
    ...overrides,
  };
}

describe('weightEntrySchema', () => {
  it('accepts a valid payload', () => {
    expect(() => weightEntrySchema.parse(valid())).not.toThrow();
  });

  it('rejects zero weight_value', () => {
    expect(() => weightEntrySchema.parse(valid({ weight_value: 0 }))).toThrow();
  });

  it('rejects negative weight_value', () => {
    expect(() => weightEntrySchema.parse(valid({ weight_value: -1 }))).toThrow();
  });

  it('accepts max weight_value 1500', () => {
    expect(() => weightEntrySchema.parse(valid({ weight_value: 1500 }))).not.toThrow();
  });

  it('rejects weight_value above 1500', () => {
    expect(() => weightEntrySchema.parse(valid({ weight_value: 1500.01 }))).toThrow();
  });

  it('accepts weight_unit lbs', () => {
    expect(weightEntrySchema.parse(valid({ weight_unit: 'lbs' })).weight_unit).toBe('lbs');
  });

  it('accepts weight_unit kg', () => {
    expect(weightEntrySchema.parse(valid({ weight_unit: 'kg' })).weight_unit).toBe('kg');
  });

  it('rejects invalid weight_unit', () => {
    expect(() => weightEntrySchema.parse(valid({ weight_unit: 'oz' }))).toThrow();
  });

  it('accepts today as observation_date', () => {
    expect(() => weightEntrySchema.parse(valid({ observation_date: TODAY }))).not.toThrow();
  });

  it('accepts a past observation_date', () => {
    expect(() => weightEntrySchema.parse(valid({ observation_date: YESTERDAY }))).not.toThrow();
  });

  it('rejects a future observation_date', () => {
    expect(() => weightEntrySchema.parse(valid({ observation_date: TOMORROW }))).toThrow();
  });

  it('accepts empty notes (undefined)', () => {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { notes: _notes, ...noNotes } = { ...valid(), notes: undefined };
    expect(() => weightEntrySchema.parse(noNotes)).not.toThrow();
  });

  it('accepts notes up to 500 chars', () => {
    expect(() => weightEntrySchema.parse(valid({ notes: 'x'.repeat(500) }))).not.toThrow();
  });

  it('rejects notes exceeding 500 chars', () => {
    expect(() => weightEntrySchema.parse(valid({ notes: 'x'.repeat(501) }))).toThrow();
  });
});
