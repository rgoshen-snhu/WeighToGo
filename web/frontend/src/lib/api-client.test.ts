import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { fetchJson } from './api-client';

// Minimal Response factory for use in fetch mocks.
function makeResponse(
  body: unknown,
  options: { status?: number; contentType?: string } = {},
): Response {
  const { status = 200, contentType = 'application/json' } = options;
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': contentType },
  });
}

describe('fetchJson', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.resolve(makeResponse({ ok: true }))),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('exports a fetchJson function', () => {
    expect(typeof fetchJson).toBe('function');
  });

  it('returns parsed JSON on a 2xx response', async () => {
    const data = await fetchJson('/api/test');
    expect(data).toEqual({ ok: true });
  });

  it('throws an error on a 4xx response', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.resolve(makeResponse({ message: 'Not found' }, { status: 404 }))),
    );
    await expect(fetchJson('/api/missing')).rejects.toThrow();
  });

  it('throws an error on a 5xx response', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.resolve(makeResponse({ message: 'Server error' }, { status: 500 }))),
    );
    await expect(fetchJson('/api/broken')).rejects.toThrow();
  });

  it('sets the Content-Type header to application/json by default', async () => {
    const mockFetch = vi.fn(() => Promise.resolve(makeResponse({ ok: true })));
    vi.stubGlobal('fetch', mockFetch);

    await fetchJson('/api/test', { method: 'POST', body: { name: 'test' } });

    const callArgs = mockFetch.mock.calls[0] as unknown as [string, RequestInit];
    const headers = callArgs[1]?.headers as Record<string, string>;
    expect(headers['Content-Type']).toBe('application/json');
  });
});
