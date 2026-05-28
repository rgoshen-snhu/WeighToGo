import { describe, expect, it } from 'vitest';
import {
  AUTH_ACCOUNT_LOCKED,
  AUTH_GENERIC_FAILURE,
  AUTH_INVALID_CREDENTIALS,
  AUTH_RATE_LIMITED,
  AUTH_REGISTER_FAILED,
} from './messages';

// Value-pinning suite for ADR-0010 auth-safe string constants.
// These tests exist so that any wording change to a constant fails here first,
// forcing a deliberate policy review rather than a silent regression.
describe('ADR-0010 auth-safe message constants', () => {
  it('AUTH_INVALID_CREDENTIALS has the correct value', () => {
    expect(AUTH_INVALID_CREDENTIALS).toBe('Invalid credentials.');
  });

  it('AUTH_ACCOUNT_LOCKED has the correct value', () => {
    expect(AUTH_ACCOUNT_LOCKED).toBe('Account is temporarily locked. Please try again later.');
  });

  it('AUTH_RATE_LIMITED has the correct value', () => {
    expect(AUTH_RATE_LIMITED).toBe('Too many attempts. Please wait a moment and try again.');
  });

  it('AUTH_REGISTER_FAILED has the correct value', () => {
    expect(AUTH_REGISTER_FAILED).toBe('The account could not be created. Please try again.');
  });

  it('AUTH_GENERIC_FAILURE has the correct value', () => {
    expect(AUTH_GENERIC_FAILURE).toBe('Something went wrong. Please try again.');
  });
});
