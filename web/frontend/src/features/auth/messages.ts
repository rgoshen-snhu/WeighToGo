/**
 * ADR-0010 — Generic Authentication Error Policy
 * User-visible auth-safe strings. Values are deliberately non-disclosive
 * (no detail about whether an account exists, the exact failure reason, etc.).
 * Import these constants — never re-type the literals inline.
 */

export const AUTH_INVALID_CREDENTIALS = 'Invalid credentials.';

export const AUTH_ACCOUNT_LOCKED = 'Account is temporarily locked. Please try again later.';

export const AUTH_RATE_LIMITED = 'Too many attempts. Please wait a moment and try again.';

export const AUTH_REGISTER_FAILED = 'The account could not be created. Please try again.';

export const AUTH_GENERIC_FAILURE = 'Something went wrong. Please try again.';
