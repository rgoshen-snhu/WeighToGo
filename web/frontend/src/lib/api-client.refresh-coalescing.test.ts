/**
 * Concurrent refresh coalescing tests (ADR-0013 / ADR-0018, GH-34).
 *
 * Verifies that two parallel requests that both receive 401 trigger exactly one
 * refresh call, not two — preventing the double-refresh that ADR-0013's
 * family-revocation policy would turn into an involuntary logout.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import {
  ApiError,
  fetchJson,
  installAuthRefreshInterceptor,
  resetAuthRefreshInterceptor,
} from './api-client';

function makeResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

const make401 = (): Response => new Response(null, { status: 401 });

describe('fetchJson concurrent refresh coalescing', () => {
  beforeEach(() => {
    resetAuthRefreshInterceptor();
  });

  afterEach(() => {
    resetAuthRefreshInterceptor();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('coalesces parallel 401 responses into a single refresh call', async () => {
    // ARRANGE
    const callLog: string[] = [];
    const refresh = vi.fn(async () => {
      callLog.push('refresh');
    });
    const onLogout = vi.fn();
    installAuthRefreshInterceptor({ refresh, onLogout });

    let fetchN = 0;
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => {
        fetchN += 1;
        callLog.push(`fetch:${fetchN}`);
        return fetchN <= 2 ? make401() : makeResponse({ ok: true });
      }),
    );

    // ACT — fire two requests concurrently so both 401s race
    const [r1, r2] = await Promise.all([
      fetchJson<{ ok: boolean }>('/api/v1/me'),
      fetchJson<{ ok: boolean }>('/api/v1/dashboard/summary'),
    ]);

    // ASSERT — exactly one refresh despite two 401s, and it happens before retries
    expect(refresh).toHaveBeenCalledTimes(1);
    expect(onLogout).not.toHaveBeenCalled();
    expect(r1).toEqual({ ok: true });
    expect(r2).toEqual({ ok: true });
    // Pin refresh-before-retry ordering: refresh must appear between the two 401s
    // and the two retries in the call log.
    expect(callLog).toEqual(['fetch:1', 'fetch:2', 'refresh', 'fetch:3', 'fetch:4']);
  });

  it('calls onLogout exactly once when concurrent refresh fails', async () => {
    // ARRANGE
    const refresh = vi.fn().mockRejectedValue(new Error('refresh failed'));
    const onLogout = vi.fn();
    installAuthRefreshInterceptor({ refresh, onLogout });

    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(make401()));

    // ACT — both requests get 401, share the same failing refresh
    const results = await Promise.allSettled([
      fetchJson('/api/v1/me'),
      fetchJson('/api/v1/dashboard/summary'),
    ]);

    // ASSERT — single refresh, single onLogout (fired in the promise chain,
    // not per-caller, so there is no double-redirect on concurrent failure)
    expect(refresh).toHaveBeenCalledTimes(1);
    expect(onLogout).toHaveBeenCalledTimes(1);
    // Both callers receive a standardised ApiError, not the raw rejection
    for (const r of results) {
      expect(r.status).toBe('rejected');
      expect((r as PromiseRejectedResult).reason).toBeInstanceOf(ApiError);
    }
  });

  it('calls onLogout once per caller when coalesced retries fail after a successful refresh', async () => {
    // ARRANGE — refresh succeeds but the retried requests both return 5xx
    const refresh = vi.fn().mockResolvedValue(undefined);
    const onLogout = vi.fn();
    installAuthRefreshInterceptor({ refresh, onLogout });

    let fetchN = 0;
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => {
        fetchN += 1;
        return fetchN <= 2 ? make401() : makeResponse({ error: 'server error' }, 500);
      }),
    );

    // ACT
    const results = await Promise.allSettled([
      fetchJson('/api/v1/me'),
      fetchJson('/api/v1/dashboard/summary'),
    ]);

    // ASSERT — documents the known N-onLogout limitation on the retry-failure
    // path (see ADR-0018 Consequences).  Refresh happens once, but each caller
    // independently calls onLogout when its own retry fails.
    expect(refresh).toHaveBeenCalledTimes(1);
    expect(onLogout).toHaveBeenCalledTimes(2);
    for (const r of results) {
      expect(r.status).toBe('rejected');
    }
  });

  it('handles a synchronously-throwing refresh as a standardised 401 ApiError', async () => {
    // refresh() is typed () => Promise<void> but a non-async implementation
    // could throw synchronously before returning a promise.
    const onLogout = vi.fn();
    installAuthRefreshInterceptor({
      refresh: () => {
        throw new Error('synchronous failure');
      },
      onLogout,
    });

    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(make401()));

    // ASSERT — caller receives standardised ApiError, not the raw sync error
    await expect(fetchJson('/api/v1/me')).rejects.toBeInstanceOf(ApiError);
    expect(onLogout).toHaveBeenCalledTimes(1);
  });
});
