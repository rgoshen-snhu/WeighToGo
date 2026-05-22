import { describe, expect, it } from 'vitest';

import { mapApiError } from './error-mapping';

describe('mapApiError', () => {
  it('returns a user-friendly string for a 401 status', () => {
    const message = mapApiError(401);
    expect(typeof message).toBe('string');
    expect(message.length).toBeGreaterThan(0);
  });

  it('returns a user-friendly string for a 409 status', () => {
    const message = mapApiError(409);
    expect(typeof message).toBe('string');
    expect(message.length).toBeGreaterThan(0);
  });

  it('returns a user-friendly string for a 422 status', () => {
    const message = mapApiError(422);
    expect(typeof message).toBe('string');
    expect(message.length).toBeGreaterThan(0);
  });

  it('returns a user-friendly string for a 500 status', () => {
    const message = mapApiError(500);
    expect(typeof message).toBe('string');
    expect(message.length).toBeGreaterThan(0);
  });

  it('returns different messages for different status codes', () => {
    expect(mapApiError(401)).not.toBe(mapApiError(500));
  });

  it('returns a fallback string for an unknown status code', () => {
    const message = mapApiError(999);
    expect(typeof message).toBe('string');
    expect(message.length).toBeGreaterThan(0);
  });
});
