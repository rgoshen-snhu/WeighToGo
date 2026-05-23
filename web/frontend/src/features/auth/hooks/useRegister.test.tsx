import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { authClient, type AuthUser } from '../api/auth-client';
import { ApiError, ValidationError } from '../../../lib/api-client';
import { AuthProvider } from '../../../contexts/AuthContext';
import { useRegister } from './useRegister';

const user: AuthUser = {
  user_id: 2,
  email: 'jane@example.com',
  display_name: 'Jane',
  created_at: '2026-05-23T00:00:00Z',
};

const validValues = {
  email: 'jane@example.com',
  password: 'Password1!valid',
  confirmPassword: 'Password1!valid',
  displayName: 'Jane',
};

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={['/register']}>
        <AuthProvider>{children}</AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe('useRegister', () => {
  beforeEach(() => {
    vi.spyOn(authClient, 'me').mockResolvedValue(null as unknown as AuthUser);
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('calls authClient.register and sets user on success', async () => {
    vi.spyOn(authClient, 'register').mockResolvedValueOnce(user);
    const { result } = renderHook(() => useRegister(), { wrapper });
    const setError = vi.fn();
    result.current.submit(validValues, setError);
    await waitFor(() => expect(result.current.status).toBe('idle'));
    expect(authClient.register).toHaveBeenCalledWith({
      email: 'jane@example.com',
      password: 'Password1!valid',
      displayName: 'Jane',
    });
  });

  it('calls setError for 422 ValidationError field errors', async () => {
    vi.spyOn(authClient, 'register').mockRejectedValueOnce(
      new ValidationError({ email: 'Email already in use' }, 'Validation failed'),
    );
    const { result } = renderHook(() => useRegister(), { wrapper });
    const setError = vi.fn();
    result.current.submit(validValues, setError);
    await waitFor(() =>
      expect(setError).toHaveBeenCalledWith('email', {
        type: 'server',
        message: 'Email already in use',
      }),
    );
  });

  it('sets formError on 409 email conflict', async () => {
    vi.spyOn(authClient, 'register').mockRejectedValueOnce(new ApiError(409, 'Conflict'));
    const { result } = renderHook(() => useRegister(), { wrapper });
    result.current.submit(validValues, vi.fn());
    await waitFor(() =>
      expect(result.current.formError).toBe('An account with this email already exists.'),
    );
  });

  it('sets generic formError on unexpected network error', async () => {
    vi.spyOn(authClient, 'register').mockRejectedValueOnce(new Error('Network error'));
    const { result } = renderHook(() => useRegister(), { wrapper });
    result.current.submit(validValues, vi.fn());
    await waitFor(() => expect(result.current.formError).toMatch(/something went wrong/i));
  });

  it('flips status to submitting while in flight', async () => {
    let resolve!: (v: AuthUser) => void;
    vi.spyOn(authClient, 'register').mockReturnValueOnce(
      new Promise((r) => {
        resolve = r;
      }),
    );
    const { result } = renderHook(() => useRegister(), { wrapper });
    result.current.submit(validValues, vi.fn());
    await waitFor(() => expect(result.current.status).toBe('submitting'));
    resolve(user);
  });
});
