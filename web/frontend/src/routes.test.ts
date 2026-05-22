import { describe, expect, it } from 'vitest';

// These imports intentionally fail until routes.tsx is created.
import { protectedRoutes, publicRoutes } from './routes';

describe('publicRoutes', () => {
  it('exports a non-empty array', () => {
    expect(Array.isArray(publicRoutes)).toBe(true);
    expect(publicRoutes.length).toBeGreaterThan(0);
  });

  it('contains an entry for /login', () => {
    const paths = publicRoutes.map((r) => r.path);
    expect(paths).toContain('/login');
  });

  it('contains an entry for /register', () => {
    const paths = publicRoutes.map((r) => r.path);
    expect(paths).toContain('/register');
  });

  it('every entry has a string path property', () => {
    for (const route of publicRoutes) {
      expect(typeof route.path).toBe('string');
    }
  });
});

describe('protectedRoutes', () => {
  it('exports a non-empty array', () => {
    expect(Array.isArray(protectedRoutes)).toBe(true);
    expect(protectedRoutes.length).toBeGreaterThan(0);
  });

  it('contains an entry for / (dashboard)', () => {
    const paths = protectedRoutes.map((r) => r.path);
    expect(paths).toContain('/');
  });

  it('contains an entry for /weight', () => {
    const paths = protectedRoutes.map((r) => r.path);
    expect(paths).toContain('/weight');
  });

  it('contains an entry for /goals', () => {
    const paths = protectedRoutes.map((r) => r.path);
    expect(paths).toContain('/goals');
  });

  it('contains an entry for /achievements', () => {
    const paths = protectedRoutes.map((r) => r.path);
    expect(paths).toContain('/achievements');
  });

  it('contains an entry for /settings', () => {
    const paths = protectedRoutes.map((r) => r.path);
    expect(paths).toContain('/settings');
  });

  it('every entry has a string path property', () => {
    for (const route of protectedRoutes) {
      expect(typeof route.path).toBe('string');
    }
  });
});
