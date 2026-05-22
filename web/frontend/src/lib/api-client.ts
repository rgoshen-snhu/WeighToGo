/**
 * Thin fetch wrapper for the Weigh to Go! API.
 *
 * Enforces JSON Content-Type on outgoing requests, parses response bodies as
 * JSON, and throws a typed error for any non-2xx response so callers can rely
 * on a single error-handling path.
 *
 * Phase 6 will extend this with:
 * - Auth token injection from AuthContext
 * - Automatic token-refresh on 401
 * - Request cancellation via AbortController
 *
 * SRS §10.3 governs the API client design.
 */

import { mapApiError } from './error-mapping';

/**
 * Error thrown when the API returns a non-2xx response.
 */
export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

interface FetchJsonOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
}

/**
 * Fetch a JSON resource from the given URL.
 *
 * Automatically sets `Content-Type: application/json` and serialises the
 * `body` option to JSON.
 *
 * @param url     - Absolute or relative URL to fetch.
 * @param options - Optional fetch options (method, body, additional headers).
 *
 * @throws {ApiError} When the response status is outside the 2xx range.
 */
export async function fetchJson<T = unknown>(
  url: string,
  options: FetchJsonOptions = {},
): Promise<T> {
  const { method = 'GET', body, headers = {} } = options;

  const requestInit: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
  };

  if (body !== undefined) {
    requestInit.body = JSON.stringify(body);
  }

  const response = await fetch(url, requestInit);

  if (!response.ok) {
    const errorMessage = mapApiError(response.status);
    throw new ApiError(response.status, errorMessage);
  }

  return response.json() as Promise<T>;
}
