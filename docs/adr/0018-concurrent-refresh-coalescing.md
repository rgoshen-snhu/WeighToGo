# ADR-0018: Concurrent Refresh Token Coalescing (extends ADR-0013)

- **Date**: 2026-05-27
- **Status**: Accepted

## Context

ADR-0013 established refresh token rotation with family revocation: every refresh consumes the token and issues a new one; if a stale token is presented, the entire family is revoked and the user is logged out. This is intentional — it prevents token theft via replay.

The M2 Web App Quality Review (2026-05-23) identified a compliance gap in the frontend API client (`web/frontend/src/lib/api-client.ts`): `handle401AndRetry` calls `interceptor.refresh()` directly on every 401 response without coalescing concurrent callers. In practice the dashboard page issues at least two concurrent requests (weight entries + dashboard summary). If the access token expires while both are in-flight, both receive 401 simultaneously and both call `interceptor.refresh()`. ADR-0013's family-revocation policy treats the second call as a replay attack, revokes the whole family, and forces a logout — during normal, authenticated use.

## Decision

Hoist a module-level variable `let inflightRefresh: Promise<void> | null = null` in `api-client.ts`. In `handle401AndRetry`:

1. If `inflightRefresh` is non-null, `await` the existing promise — join the in-flight refresh.
2. If `inflightRefresh` is null, start a new refresh: `inflightRefresh = interceptor.refresh().finally(() => { inflightRefresh = null; })`.
3. After the promise settles (success or failure), proceed with existing logic — retry the request on success, call `onLogout` and throw on failure.

The `.finally()` clears `inflightRefresh` after every settle so the next 401 (minutes later, after a new access token also expires) starts a fresh refresh rather than awaiting a stale, already-settled promise.

All concurrent callers share both the success and the failure outcome of the single in-flight refresh. On failure, `onLogout` is called **once** — inside the shared promise's `.catch()` handler — regardless of how many callers are coalesced. This prevents the double-redirect that would result from each caller independently calling `onLogout`.

## Rationale

**Why a module-level promise rather than a flag or semaphore?**
A boolean flag would still require each concurrent caller to poll until the flag clears, introducing timing complexity. A promise is the natural JavaScript primitive for "join this in-progress operation." Any number of callers can `await` the same promise, receiving the outcome exactly once when it settles, with no polling.

**Why `.finally()` instead of `.then()` / `.catch()` to clear the variable?**
`.finally()` runs on both resolution and rejection, ensuring the module-level slot is always freed. Using `.then()` only would leave `inflightRefresh` set forever after a failed refresh, blocking all future retries.

**Why not store the promise on the interceptor object?**
The interceptor is replaced by `installAuthRefreshInterceptor` each time the auth context mounts. Storing the in-flight promise on the module-level variable keeps it independent of the interceptor lifecycle — a new interceptor install doesn't orphan an in-flight promise.

**Why module-level rather than inside a closure or class?**
`api-client.ts` exports a set of functions operating on shared module state (`interceptor`). The in-flight promise follows the same pattern. Module-level state is appropriate here: there is one API client per tab, and cross-tab coordination is explicitly out of scope (each tab's auth state is independent).

**Failure-mode semantics (refresh fails):** `onLogout` fires once, inside the `.catch()` of the shared `inflightRefresh` promise. All coalesced callers receive the same rejection, each throwing `ApiError(401)` — but `onLogout` is not called again per caller.

**Failure-mode semantics (refresh succeeds, retry fails):** Each coalesced caller independently retries its original request after the shared refresh completes. If a retry returns a non-2xx non-422 status, the caller calls `onLogout` independently. With N coalesced callers all receiving 401-on-retry, this produces N `onLogout` calls. This is an accepted limitation for the M2 scope (the dashboard issues two concurrent requests, so N≤2 in practice); `onLogout` clearing auth state and redirecting is idempotent so double-calling it is harmless.

## Consequences

- **Positive**: ADR-0013 compliance restored. Concurrent 401s no longer trigger multiple refresh calls. Normal dashboard usage no longer involuntarily logs the user out. `onLogout` fires exactly once on refresh failure regardless of concurrent caller count.
- **Negative (retry-failure)**: If the shared refresh succeeds but the coalesced retries then fail with a non-2xx status, each caller independently calls `onLogout`. For the current dashboard pattern (two requests), this means at most two `onLogout` calls on an unlikely double-retry-failure. Since `onLogout` is idempotent (clears auth state, redirects), this is acceptable. A future hardening pass could add a one-shot gate around the post-retry `onLogout` calls.
- **Negative (same-tick scope)**: Coalescing only prevents double-refresh when both 401s arrive before the first refresh's `.finally` clears the slot — roughly within the same microtask batch. Two 401s arriving hundreds of milliseconds apart (e.g. a polling widget and a user action) will each trigger their own refresh. This is acceptable for M2's dashboard-request pattern; future polling features may need a longer-lived lock (e.g. a `sessionStorage` flag with a TTL).
- **Follow-ups**: If cross-tab coordination is ever required (e.g. shared-worker auth), a BroadcastChannel or shared storage approach would be needed. That is out of scope for M2.

## Alternatives Considered

- **Debounce / throttle the refresh call** — rejected because debounce introduces an arbitrary delay before the first refresh, degrading UX. Coalescing has zero added latency for the first caller.
- **Backend: make refresh idempotent** — rejected because ADR-0013's single-use policy is a deliberate security property. Weakening it to tolerate replay would undermine the family-revocation guarantee.
- **Lock via localStorage** — rejected because it is a cross-tab primitive; the problem being solved is within a single tab. Adding cross-tab locking for a within-tab problem is over-engineering.
