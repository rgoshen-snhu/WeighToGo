import { act, render, renderHook, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { AuthProvider, useAuth } from './AuthContext';

// Minimal user fixture used across tests.
const stubUser = {
  id: '1',
  email: 'test@example.com',
  displayName: 'Test User',
};

describe('useAuth', () => {
  it('throws when used outside AuthProvider', () => {
    // Suppress the expected console.error from React.
    const spy = vi
      .spyOn(console, 'error')
      .mockImplementation(() => undefined);
    expect(() => renderHook(() => useAuth())).toThrow(
      /AuthProvider/,
    );
    spy.mockRestore();
  });

  it('provides user as null initially', () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });
    expect(result.current.user).toBeNull();
  });

  it('provides isAuthenticated as false when there is no user', () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });
    expect(result.current.isAuthenticated).toBe(false);
  });

  it('exposes a login function', () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });
    expect(typeof result.current.login).toBe('function');
  });

  it('exposes a logout function', () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });
    expect(typeof result.current.logout).toBe('function');
  });

  it('login sets the user and isAuthenticated to true', () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });
    act(() => {
      result.current.login(stubUser);
    });
    expect(result.current.user).toEqual(stubUser);
    expect(result.current.isAuthenticated).toBe(true);
  });

  it('logout clears the user and sets isAuthenticated to false', () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });
    act(() => {
      result.current.login(stubUser);
    });
    act(() => {
      result.current.logout();
    });
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });
});

describe('AuthProvider', () => {
  it('renders children', () => {
    render(
      <AuthProvider>
        <span>child content</span>
      </AuthProvider>,
    );
    expect(screen.getByText('child content')).toBeInTheDocument();
  });
});
