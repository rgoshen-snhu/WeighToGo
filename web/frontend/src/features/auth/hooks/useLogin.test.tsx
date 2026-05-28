import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { authClient, type AuthUser } from '../api/auth-client';
import { ApiError, ValidationError } from '../../../lib/api-client';
import { AuthProvider } from '../../../contexts/AuthContext';
import { useLogin } from './useLogin';
import {
  AUTH_INVALID_CREDENTIALS,
  AUTH_ACCOUNT_LOCKED,
  AUTH_RATE_LIMITED,
  AUTH_GENERIC_FAILURE,
} from '../messages';

const user: AuthUser = {
  user_id: 1,
  email: 'a@b.co',
  display_name: 'A',
  created_at: '2026-05-23T00:00:00Z',
};

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={['/login']}>
        <AuthProvider>{children}</AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe('useLogin', () => {
  beforeEach(() => {
    vi.spyOn(authClient, 'me').mockResolvedValue(null as unknown as AuthUser);
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  const makeHelpers = () => ({ setError: vi.fn(), resetField: vi.fn() });

  it('calls authClient.login and sets user on success', async () => {
    vi.spyOn(authClient, 'login').mockResolvedValueOnce(user);
    const { result } = renderHook(() => useLogin(), { wrapper });
    result.current.submit({ email: 'a@b.co', password: 'pass' }, makeHelpers());
    await waitFor(() => expect(result.current.status).toBe('idle'));
    expect(authClient.login).toHaveBeenCalledWith({ email: 'a@b.co', password: 'pass' });
  });

  it('sets formError to AUTH_INVALID_CREDENTIALS on 401', async () => {
    vi.spyOn(authClient, 'login').mockRejectedValueOnce(new ApiError(401, 'Unauthorized'));
    const { result } = renderHook(() => useLogin(), { wrapper });
    result.current.submit({ email: 'a@b.co', password: 'wrong' }, makeHelpers());
    await waitFor(() => expect(result.current.formError).toBe(AUTH_INVALID_CREDENTIALS));
  });

  it('sets formError to AUTH_ACCOUNT_LOCKED on 423', async () => {
    vi.spyOn(authClient, 'login').mockRejectedValueOnce(new ApiError(423, 'Locked'));
    const { result } = renderHook(() => useLogin(), { wrapper });
    result.current.submit({ email: 'a@b.co', password: 'wrong' }, makeHelpers());
    await waitFor(() => expect(result.current.formError).toBe(AUTH_ACCOUNT_LOCKED));
  });

  it('sets formError to AUTH_RATE_LIMITED on 429', async () => {
    vi.spyOn(authClient, 'login').mockRejectedValueOnce(new ApiError(429, 'Too many'));
    const { result } = renderHook(() => useLogin(), { wrapper });
    result.current.submit({ email: 'a@b.co', password: 'wrong' }, makeHelpers());
    await waitFor(() => expect(result.current.formError).toBe(AUTH_RATE_LIMITED));
  });

  it('calls setError for ValidationError field errors', async () => {
    vi.spyOn(authClient, 'login').mockRejectedValueOnce(
      new ValidationError({ email: 'bad email' }, 'Validation failed'),
    );
    const { result } = renderHook(() => useLogin(), { wrapper });
    const helpers = makeHelpers();
    result.current.submit({ email: 'bad', password: 'pass' }, helpers);
    await waitFor(() =>
      expect(helpers.setError).toHaveBeenCalledWith('email', {
        type: 'server',
        message: 'bad email',
      }),
    );
  });

  it('sets AUTH_GENERIC_FAILURE on ApiError with unhandled status (e.g. 500)', async () => {
    vi.spyOn(authClient, 'login').mockRejectedValueOnce(new ApiError(500, 'Server error'));
    const { result } = renderHook(() => useLogin(), { wrapper });
    result.current.submit({ email: 'a@b.co', password: 'pass' }, makeHelpers());
    await waitFor(() => expect(result.current.formError).toBe(AUTH_GENERIC_FAILURE));
  });

  it('sets AUTH_GENERIC_FAILURE on non-ApiError (e.g. network failure)', async () => {
    vi.spyOn(authClient, 'login').mockRejectedValueOnce(new Error('Network failure'));
    const { result } = renderHook(() => useLogin(), { wrapper });
    result.current.submit({ email: 'a@b.co', password: 'pass' }, makeHelpers());
    await waitFor(() => expect(result.current.formError).toBe(AUTH_GENERIC_FAILURE));
  });

  it('isPending flips status to submitting while in flight', async () => {
    let resolve!: (v: AuthUser) => void;
    vi.spyOn(authClient, 'login').mockReturnValueOnce(
      new Promise((r) => {
        resolve = r;
      }),
    );
    const { result } = renderHook(() => useLogin(), { wrapper });
    result.current.submit({ email: 'a@b.co', password: 'pass' }, makeHelpers());
    await waitFor(() => expect(result.current.status).toBe('submitting'));
    resolve(user);
  });
});
