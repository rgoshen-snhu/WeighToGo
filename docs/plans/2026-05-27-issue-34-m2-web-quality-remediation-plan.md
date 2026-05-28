# Issue #34 — M2 Web App Quality Remediation Plan

**Date:** 2026-05-27
**Issue:** [#34 — Remediate M2 Web App Quality Review blocking findings](https://github.com/rgoshen-snhu/WeightToGo/issues/34)
**Authoritative review:** `docs/standards/M2_WEB_APP_QUALITY.md`
**Status:** Approved (brainstorming complete; ready for execution)
**Scope target:** M2 Web App quality-complete sign-off per the 2026-05-23 review

---

## 1. Context and Goal

The M2 Web App Quality Review (2026-05-23) identified five blocking findings that prevent the web app from being declared M2 quality-complete:

- Two SRS security NFR gaps: NFR-S-10 (security headers — HSTS, CSP) and NFR-S-9 (CSRF Origin/Referer validation on state-changing requests).
- One ADR-0013 contract violation: the frontend refresh interceptor can replay a one-time refresh token under concurrent 401s, forcing users to log out during normal use.
- One ADR-0010 compliance regression: the registration UI reveals account existence to anyone using the form, violating the documented generic-authentication-error policy.
- One SRS NFR-A-5 accessibility gap: weight table action controls fall below the 44 × 44 px target-size requirement.

The reviewer also called out documentation version drift as a sixth recommended remediation item (`SRS §3.1 FR-03` references in code while the current SRS uses `FR-A-*`, and React Router v6 references in SRS prose while code is on v7). This plan promotes that item from "follow-up" to formal F6 and updates issue #34's task list to match.

**Definition of done:** all six findings closed with TDD-backed evidence, the M2 quality review doc carries a dated resolution section, and the web app passes its full test and lint suite on `main` after the closeout PR merges.

---

## 2. Scope

### 2.1 In scope

| ID | Title | Stack | Primary files |
|---|---|---|---|
| F1 | Security headers (HSTS + CSP) | Backend | `web/backend/src/weighttogo/main.py`, new tests in `tests/test_security_headers.py` |
| F2 | CSRF Origin/Referer validation | Backend | `web/backend/src/weighttogo/main.py`, new module `interface/middleware/csrf.py`, new tests in `tests/test_csrf_middleware.py` |
| F3 | Coalesce concurrent refresh | Frontend | `web/frontend/src/lib/api-client.ts`, new tests in `src/lib/__tests__/api-client.refresh-coalescing.test.ts` |
| F4 | Remove email-existence disclosure | Frontend | `web/frontend/src/features/auth/hooks/useRegister.ts`, existing test update |
| F5 | Weight table action target size | Frontend | `web/frontend/src/features/weight/components/WeightEntryTable.tsx`, component test + Playwright assertion |
| F6 | Documentation version drift cleanup | Docs | `web/frontend/src/features/auth/components/RegisterForm.tsx` comments, `docs/specs/WeighToGo_Web_SRS_v2.md`, any other code-comment SRS drift discovered during F1–F5 |

### 2.2 Out of scope

The following appear in the M2 review but are **not** part of this plan:

- **Dashboard slice expansion to full bounded context.** The review explicitly classifies the dashboard's interface+application-only structure as an intentional M2 exception, not a finding.
- **Injectable clock for date-boundary tests.** The review notes this as a future hardening pass under "Arithmetic Operations," not a blocking finding.
- **Frontend import-boundary enforcement tool.** The review notes the absence of an import-linter equivalent on the frontend but classifies it "not a blocker for M2."
- **Production deployment hardening beyond the SRS-mandated header set.** E.g., CAA records, certificate pinning, WAF — out of scope.

### 2.3 Updating issue #34

Before execution begins, issue #34's task list must be amended to include the F6 checkbox:

> - [ ] **F6 — Documentation version drift cleanup:** Update `RegisterForm.tsx` SRS §3.1 FR-03 comment to current FR-A-* mapping; update SRS prose references to React Router v7. Audit any other code-comment SRS drift surfaced during F1–F5 work.

This amendment is the first action of the execution phase; it does not change scope direction, only documentation.

---

## 3. Delivery Model

### 3.1 Branching

All work cuts from `main`. The currently-existing `feature/issue-34-m2-web-quality-remediation` branch is **abandoned** in favor of the structured branch set below.

| Sequence | Branch | Purpose |
|---|---|---|
| 0 | `feature/m2-quality-review-doc` | Lands the staged `docs/standards/M2_WEB_APP_QUALITY.md` to `main` so subsequent finding PRs can reference it. Docs-only, no code, no tests. |
| 1 | `feature/issue-34-F1-security-headers` | F1 implementation + ADR-0016. |
| 2 | `feature/issue-34-F2-csrf-origin-referer` | F2 implementation + ADR-0017. |
| 3 | `feature/issue-34-F3-refresh-coalescing` | F3 implementation + ADR-0018. |
| 4 | `feature/issue-34-F4-generic-register-error` | F4 implementation. |
| 5 | `feature/issue-34-F5-action-target-size` | F5 implementation + DDR-0004. |
| 6 | `feature/issue-34-F6-doc-drift-cleanup` | F6 documentation fixes. |
| 7 | `feature/issue-34-closeout` | Appends dated "Resolution Review" section to `M2_WEB_APP_QUALITY.md` with each merge SHA. |

PRs may run in parallel because each branch touches a disjoint set of files. Recommended merge order matches the table above; closeout (PR 7) is the only PR with a hard dependency (it references the six prior merge SHAs).

### 3.2 Commit discipline per finding

Each finding follows a strict Red → Green → Refactor cycle, expressed as separate commits:

```
test(F1): add failing security headers regression test (GH-34)
feat(F1): emit HSTS and path-aware CSP per SRS NFR-S-10 (GH-34)
refactor(F1): extract security header constants (GH-34)   # optional
docs(F1): add ADR-0016 security header policy (GH-34)
```

The Refactor commit is optional and omitted when no cleanup is warranted. The ADR/DDR commit lands on the same branch but as a separate commit so the implementation diff stays readable. Each commit references issue #34 via `(GH-34)` suffix per repo convention.

### 3.3 Test gates before every push

Before pushing each branch, run the full local gate matching CI. Backend (from `web/backend`):

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
```

Frontend (from `web/frontend`):

```bash
npm run lint
npm run format:check
npm run typecheck
npm run test:ci
```

Playwright runs locally for F1, F2 (verify E2E still passes against new middleware), F3 (verify concurrent-401 path doesn't break dashboard), F5 (target-size assertion):

```bash
npm run test:e2e
```

---

## 4. Per-Finding Implementation Outlines

Each subsection below specifies the failing test to write first (Red), the minimal implementation to make it pass (Green), and any optional cleanup (Refactor).

### 4.1 F1 — Security headers (HSTS + CSP) — NFR-S-10

**Problem.** `web/backend/src/weighttogo/main.py:64-77` emits four of the six SRS-required headers (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`). It omits `Strict-Transport-Security` and `Content-Security-Policy`.

**Solution.**

- Add HSTS conditionally on `settings.environment == "production"`. Value: `max-age=31536000; includeSubDomains`. Out of `production`, omit the header (matches existing `cookie_secure` env-awareness pattern).
- Add CSP unconditionally with a path-aware policy:
  - **Default policy (all responses):** `default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'`. This is functionally free for JSON responses and maximally protective against XSS / clickjacking on any HTML that escapes by accident.
  - **Override for `/api/docs` and `/api/redoc`:** `default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; img-src 'self' data: https://fastapi.tiangolo.com; connect-src 'self'`. Allows Swagger UI / ReDoc to load their CDN assets.

**Red test (`tests/test_security_headers.py`):**

```python
def test_health_response_has_full_required_security_header_set():
    # ARRANGE / ACT
    response = client.get("/health")
    # ASSERT — all six SRS-required headers present
    assert "Strict-Transport-Security" in response.headers  # env-aware
    assert "Content-Security-Policy" in response.headers
    assert "X-Content-Type-Options" in response.headers
    assert "X-Frame-Options" in response.headers
    assert "Referrer-Policy" in response.headers
    assert "Permissions-Policy" in response.headers

def test_csp_default_policy_is_strict_for_json_responses():
    response = client.get("/health")
    csp = response.headers["Content-Security-Policy"]
    assert "default-src 'none'" in csp
    assert "frame-ancestors 'none'" in csp

def test_csp_override_allows_swagger_cdn_for_docs_endpoint():
    response = client.get("/api/docs")
    csp = response.headers["Content-Security-Policy"]
    assert "cdn.jsdelivr.net" in csp

def test_hsts_emitted_only_in_production(monkeypatch):
    # ARRANGE — non-production environment
    monkeypatch.setenv("ENVIRONMENT", "development")
    # ACT
    response = client.get("/health")
    # ASSERT
    assert "Strict-Transport-Security" not in response.headers
```

The test file uses the existing pytest fixtures pattern. Tests use `monkeypatch` for env-specific cases since the codebase uses `get_settings()`.

**Green implementation sketch (in `main.py` middleware).** Inline pseudocode:

```python
DEFAULT_CSP = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
DOCS_CSP = (
    "default-src 'self'; "
    "script-src 'self' https://cdn.jsdelivr.net; "
    "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
    "img-src 'self' data: https://fastapi.tiangolo.com; "
    "connect-src 'self'"
)
DOCS_PATHS = ("/api/docs", "/api/redoc", "/api/v1/openapi.json")

# In middleware:
response.headers["Content-Security-Policy"] = (
    DOCS_CSP if request.url.path in DOCS_PATHS else DEFAULT_CSP
)
if settings.environment == "production":
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
```

**Refactor.** Extract `DEFAULT_CSP`, `DOCS_CSP`, `DOCS_PATHS`, and the HSTS value to a small `weighttogo/shared/security_headers.py` module if the inline literals push the middleware over ~30 lines.

**ADR-0016.** Title: "Security header policy (HSTS + CSP)." Documents the path-aware CSP decision, the rejected alternatives (env-aware uniform, permissive uniform, production-only enforcement), and the trade-off accepted (5 lines of path-branch logic vs. cross-environment consistency).

**Acceptance:**
- All six SRS-required headers present on representative endpoints.
- HSTS gated on `production` env.
- CSP differentiated by path.
- Backend test suite passes (existing 277 tests plus new header tests).
- mypy/ruff clean.

---

### 4.2 F2 — CSRF Origin/Referer validation — NFR-S-9

**Problem.** `web/backend/src/weighttogo/main.py` configures CORS and `SameSite=Strict` cookies but has no server-side `Origin`/`Referer` validation on state-changing requests, which the SRS requires as a defense-in-depth layer beyond SameSite.

**Solution.**

- Create a new middleware module at `web/backend/src/weighttogo/interface/middleware/csrf.py` (matches Hexagonal "outer-layer adapter" placement).
- Middleware behavior:
  - Safe methods (`GET`, `HEAD`, `OPTIONS`) bypass.
  - Unsafe methods (`POST`, `PUT`, `DELETE`, `PATCH`) check `Origin` first; if absent, fall back to `Referer` (validate origin portion of the URL only).
  - If neither header is present, or the value doesn't match any entry in `cors_allowed_origins` (parsed the same way `_get_cors_origins` parses it in `main.py`), return `403` with an RFC 7807 body: `{"type": "about:blank", "title": "Forbidden", "status": 403, "detail": "Origin or Referer required and must match an allowed origin."}`.
- Register in `main.py` **before** the existing `CORSMiddleware` call so CORS wraps it (Starlette applies middleware in reverse registration order — later `add_middleware` calls run outermost). This guarantees CORS handles `OPTIONS` preflight before CSRF sees the request, even though CSRF independently exempts safe methods as a defensive measure.

**Allowed-origin source.** Reuses `Settings.cors_allowed_origins`. Single source of truth — CORS and CSRF cannot drift out of sync.

**Red tests (`tests/test_csrf_middleware.py`):**

```python
def test_post_with_allowed_origin_header_passes():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "x@y.z", "password": "..."},
        headers={"Origin": "http://localhost:5173"},
    )
    assert response.status_code != 403

def test_post_with_missing_origin_and_referer_is_forbidden():
    # No Origin, no Referer
    response = client.post("/api/v1/auth/login", json={...})
    assert response.status_code == 403
    assert response.json()["title"] == "Forbidden"

def test_post_with_disallowed_origin_is_forbidden():
    response = client.post(
        "/api/v1/auth/login",
        json={...},
        headers={"Origin": "https://evil.example"},
    )
    assert response.status_code == 403

def test_post_falls_back_to_referer_when_origin_missing():
    response = client.post(
        "/api/v1/auth/login",
        json={...},
        headers={"Referer": "http://localhost:5173/login"},
    )
    assert response.status_code != 403

def test_get_request_bypasses_csrf_check():
    response = client.get("/health")
    assert response.status_code == 200

def test_options_preflight_bypasses_csrf_check():
    response = client.options("/api/v1/weight-entries")
    assert response.status_code in (200, 204)
```

**Green implementation sketch:**

```python
# interface/middleware/csrf.py
from urllib.parse import urlparse
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from weighttogo.config import get_settings

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

class CsrfOriginRefererMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in SAFE_METHODS:
            return await call_next(request)

        allowed = {o.strip() for o in get_settings().cors_allowed_origins.split(",") if o.strip()}
        origin = request.headers.get("origin")
        referer = request.headers.get("referer")

        candidate = origin or (
            f"{urlparse(referer).scheme}://{urlparse(referer).netloc}" if referer else None
        )

        if candidate is None or candidate not in allowed:
            return JSONResponse(
                status_code=403,
                content={
                    "type": "about:blank",
                    "title": "Forbidden",
                    "status": 403,
                    "detail": "Origin or Referer required and must match an allowed origin.",
                },
                media_type="application/problem+json",
            )
        return await call_next(request)
```

**Playwright compatibility.** Playwright spawns Chromium which sends `Origin: http://localhost:5173` (or whichever frontend dev origin). That origin is already in `cors_allowed_origins`, so the middleware is transparent to E2E. Verify in the F2 PR by running `npm run test:e2e` locally before pushing.

**Rate-limit interaction.** Rate limiting is disabled in Playwright (`RATE_LIMIT_ENABLED=false`); CSRF middleware does not depend on rate-limit state and vice versa, so no interaction.

**Refactor.** None expected. Module stays small.

**ADR-0017.** Title: "CSRF Origin/Referer validation for state-changing requests." Documents: defense-in-depth alongside SameSite, allowed-origin source decision (reuse CORS list), header check order (Origin → Referer), safe-method exemption, rejected alternatives (separate setting, hybrid).

**Acceptance:**
- All four cases tested (allowed pass, missing fail, invalid fail, referer fallback pass) plus safe-method exemption.
- Playwright suite still green.
- Backend test suite green.

---

### 4.3 F3 — Coalesce concurrent refresh — ADR-0013 compliance

**Problem.** `web/frontend/src/lib/api-client.ts:90-101` calls `interceptor.refresh()` on every 401 without coalescing. Two concurrent 401s call refresh twice; ADR-0013 makes refresh tokens single-use and revokes the whole family on the second call, so users get logged out during normal use (e.g., dashboard + weight queries refetching together after access-token expiry).

**Solution.**

- Hoist a module-level `let inflightRefresh: Promise<void> | null = null;` in `api-client.ts`.
- In `handle401AndRetry`, if `inflightRefresh` is non-null, `await` it; otherwise create one by calling `interceptor.refresh()` and store the promise. Clear the promise in a `.finally()` so the next 401 starts a fresh refresh.
- Same retry logic as today after the refresh completes (or throws).

**Red test (`src/lib/__tests__/api-client.refresh-coalescing.test.ts`):**

```typescript
describe('fetchJson concurrent refresh', () => {
  it('coalesces parallel 401 responses into a single refresh call', async () => {
    // ARRANGE
    const refresh = vi.fn().mockResolvedValue(undefined);
    const onLogout = vi.fn();
    installAuthRefreshInterceptor({ refresh, onLogout });

    let firstCall = true;
    global.fetch = vi.fn(async (_url, _init) => {
      // First two calls (parallel) return 401; subsequent retries return 200
      if (firstCall) {
        firstCall = false;
        return new Response(null, { status: 401 });
      }
      return new Response(JSON.stringify({ ok: true }), { status: 200 });
    });

    // ACT — fire two concurrent requests that will both 401
    const [r1, r2] = await Promise.all([
      fetchJson('/api/v1/me'),
      fetchJson('/api/v1/dashboard/summary'),
    ]);

    // ASSERT
    expect(refresh).toHaveBeenCalledTimes(1);
    expect(onLogout).not.toHaveBeenCalled();
    expect(r1).toEqual({ ok: true });
    expect(r2).toEqual({ ok: true });
  });

  it('calls onLogout exactly once when concurrent refresh fails', async () => {
    const refresh = vi.fn().mockRejectedValue(new Error('refresh failed'));
    const onLogout = vi.fn();
    installAuthRefreshInterceptor({ refresh, onLogout });
    global.fetch = vi.fn(async () => new Response(null, { status: 401 }));

    await expect(
      Promise.all([fetchJson('/api/v1/me'), fetchJson('/api/v1/dashboard/summary')]),
    ).rejects.toBeInstanceOf(ApiError);

    expect(refresh).toHaveBeenCalledTimes(1);
    expect(onLogout).toHaveBeenCalledTimes(1);
  });
});
```

The exact fetch-mocking shape will be adapted to the existing test conventions in the api-client test file. The behavior assertions above are the contract.

**Green implementation sketch:**

```typescript
let inflightRefresh: Promise<void> | null = null;

async function handle401AndRetry<T>(url: string, init: RequestInit): Promise<T> {
  const isRefreshEndpoint = url.includes('/api/v1/auth/refresh');
  if (!interceptor || isRefreshEndpoint) {
    interceptor?.onLogout();
    throw new ApiError(401, mapApiError(401));
  }
  try {
    if (inflightRefresh === null) {
      inflightRefresh = interceptor.refresh().finally(() => {
        inflightRefresh = null;
      });
    }
    await inflightRefresh;
  } catch {
    interceptor.onLogout();
    throw new ApiError(401, mapApiError(401));
  }
  // ... existing retry logic unchanged
}
```

The `.finally()` clears the promise after every refresh — success or failure — so the next 401 (e.g., minutes later) starts a fresh refresh, not the stale one. The `await` shares both success and rejection across all concurrent callers.

**Verify existing 401-retry tests still pass.** The previous tests asserted single-401-then-retry behavior; this change preserves that path when `inflightRefresh` is null.

**Refactor.** Consider extracting the coalescing into a small `getOrStartRefresh()` helper if the inline code adds clutter. Optional.

**ADR-0018.** Title: "Concurrent refresh coalescing (extends ADR-0013)." Documents: motivation (one-time refresh tokens + family revocation make racing refresh fatal), mechanism (module-level promise), failure-mode semantics (both callers see the same outcome — both succeed or both reject), no client-side persistence (single tab; cross-tab coalescing is out of scope).

**Acceptance:**
- Two concurrent 401s trigger exactly one refresh call; both retries succeed.
- Failure path: exactly one `onLogout` even with concurrent failure.
- Existing 401-retry tests remain green.

---

### 4.4 F4 — Remove email-existence disclosure — ADR-0010 compliance

**Problem.** `web/frontend/src/features/auth/hooks/useRegister.ts:38` maps HTTP 409 to `'An account with this email already exists.'`, which confirms account existence on the client even though the backend returns a generic body. This contradicts ADR-0010 and SRS FR-A-1 / FR-A-9.

**Solution.** Replace the 409-specific branch with the same generic message used for all other non-validation errors.

**Red test.** Update the existing register-hook test that currently asserts the specific account-exists wording. Find it via:

```bash
grep -rn "An account with this email already exists" web/frontend/src
```

Expected location: `web/frontend/src/features/auth/hooks/__tests__/useRegister.test.tsx` (or similar). Rewrite the assertion:

```typescript
it('shows a generic creation-failure message on HTTP 409', async () => {
  // ARRANGE — mock authClient.register to reject with 409 ApiError
  // ACT — call submit
  // ASSERT
  expect(result.current.formError).toBe('The account could not be created with those details.');
});
```

The test should fail in the Red phase because the current code still sets the old message.

**Green implementation.** In `useRegister.ts:37-39`:

```typescript
if (error instanceof ApiError) {
  setFormError('The account could not be created with those details.');
} else {
  setFormError('Something went wrong. Please try again.');
}
```

The `error.status === 409` branch collapses into the general `ApiError` branch — same message for any non-validation API error during registration.

**No ADR.** This is a direct compliance fix against ADR-0010 (which already documents the policy). The PR description should cite ADR-0010 by number.

**Acceptance:**
- 409 response from backend produces generic message in `formError`.
- Field-level validation (422 path) still works.
- No registration test asserts the old wording.

---

### 4.5 F5 — Weight table action target size — NFR-A-5

**Problem.** `web/frontend/src/features/weight/components/WeightEntryTable.tsx:68-87` uses `IconButton size="small"` for Edit and Delete actions. Small `IconButton` is 32 × 32 px (icon-only) or close to it with the inline text spans — below the SRS-required 44 × 44 px touch target. The inline `<span>Edit</span>` / `<span>Delete</span>` inside an `IconButton` is also non-idiomatic.

**Solution.** Convert both actions to `MUI Button` with `startIcon`. Default `Button` size is `medium` with a minimum height of 36.5 px; we'll explicitly set `sx={{ minHeight: 44 }}` to guarantee the 44 px floor regardless of MUI version drift.

**Red tests.**

Component test (`WeightEntryTable.test.tsx`):

```typescript
it('renders edit and delete action buttons meeting 44px minimum target size', () => {
  // ARRANGE
  render(<WeightEntryTable entries={[oneEntry]} onDelete={vi.fn()} />);
  // ACT — query by accessible name
  const editBtn = screen.getByRole('link', { name: /edit entry from/i });
  const deleteBtn = screen.getByRole('button', { name: /delete entry from/i });
  // ASSERT — getBoundingClientRect returns 0 in jsdom; instead assert sx-derived inline style or class
  // Preferred: read computed minHeight from style or rely on a data attribute that the sx prop forwards.
  expect(editBtn).toHaveStyle('min-height: 44px');
  expect(deleteBtn).toHaveStyle('min-height: 44px');
});
```

If jsdom can't resolve MUI's emotion-injected styles reliably, fall back to asserting the component renders `Button` (not `IconButton`) via a role check or class assertion. The Playwright assertion below is the authoritative gate.

Playwright assertion (in the existing dashboard or weight spec):

```typescript
test('weight table action buttons meet 44px target size', async ({ page }) => {
  await page.goto('/');
  // assume at least one entry exists from test data setup
  const editButton = page.getByRole('link', { name: /edit entry from/i }).first();
  const box = await editButton.boundingBox();
  expect(box?.height).toBeGreaterThanOrEqual(44);
  expect(box?.width).toBeGreaterThanOrEqual(44);
  // same for delete
});
```

**Green implementation.** In `WeightEntryTable.tsx:67-88`, replace the two `IconButton` blocks with:

```tsx
<Button
  component={Link}
  to={`/weight/${entry.entry_id}/edit`}
  aria-label={`Edit entry from ${entry.observation_date}`}
  size="medium"
  variant="outlined"
  startIcon={<EditIcon />}
  sx={{ minHeight: 44, mr: 1 }}
>
  Edit
</Button>
<Button
  onClick={() => onDelete(entry.entry_id)}
  aria-label={`Delete entry from ${entry.observation_date}`}
  size="medium"
  variant="outlined"
  color="error"
  startIcon={<DeleteIcon />}
  sx={{ minHeight: 44 }}
>
  Delete
</Button>
```

Drop the `Tooltip` wrappers (not needed when text label is visible) and the inline `<span style={{ marginLeft: 4 }}>` spans (replaced by `startIcon`).

**Refactor.** Extract a small `ActionButtonsCell` sub-component if the JSX in the row gets unwieldy. Optional.

**DDR-0004.** Title: "Weight table action button conversion from IconButton to Button." Documents: visual change (circular icon-only → outlined button with icon + label), accessibility motivation (44 px target), idiomatic MUI usage. Includes before/after screenshots if practical.

**Acceptance:**
- Component test asserts 44 px minimum (best-effort in jsdom).
- Playwright `boundingBox()` confirms ≥ 44 × 44.
- Visual change reviewed against DDR-0004.
- Existing weight-table tests still pass after Tooltip/span removal.

---

### 4.6 F6 — Documentation version drift cleanup

**Problem.** Code comments and SRS prose reference outdated identifiers and versions:

- `web/frontend/src/features/auth/components/RegisterForm.tsx` references `SRS §3.1 FR-03`; the current SRS uses `FR-A-*` identifiers.
- Some SRS sections in `docs/specs/WeighToGo_Web_SRS_v2.md` mention React Router v6 while the codebase is on v7.

**Solution.**

- Grep the web codebase for stale references (Darwin BSD `grep` requires `-E` for alternation):

  ```bash
  grep -rEn "FR-0[0-9]|react-router-dom v6|React Router v6" web/ docs/
  grep -rn "§3\." docs/specs/   # SRS section refs may have moved under FR-A-*
  ```

- For each hit, replace with the current identifier. For `RegisterForm.tsx`, confirm the correct FR-A-* mapping by reading the current SRS section on registration (FR-A-1 likely).
- In `WeighToGo_Web_SRS_v2.md`, update React Router version references to v7.
- Any additional drift surfaced during F1–F5 work gets folded into this PR.

**No tests required.** This is a pure documentation/comment PR. The gate is `ruff`/`eslint`/`prettier` clean and a manual diff review.

**No ADR/DDR.**

**Acceptance:**
- All known stale references updated.
- Grep returns zero hits for the patterns above (or a documented justification for residual hits).
- Lint clean on the changed files.

---

## 5. Closeout (PR 7)

After F1–F6 merge, `feature/issue-34-closeout`:

- Appends a new section to `docs/standards/M2_WEB_APP_QUALITY.md`:

```markdown
## Resolution Review — YYYY-MM-DD

| Finding | Status | PR | Commit |
|---|---|---|---|
| F1 — Security headers (HSTS + CSP) | Resolved | #NN | `<sha>` |
| F2 — CSRF Origin/Referer | Resolved | #NN | `<sha>` |
| F3 — Refresh coalescing | Resolved | #NN | `<sha>` |
| F4 — Generic register error | Resolved | #NN | `<sha>` |
| F5 — Action target size | Resolved | #NN | `<sha>` |
| F6 — Documentation drift | Resolved | #NN | `<sha>` |

**Verification:** full backend (`pytest`, `ruff`, `mypy`) and frontend (`test:ci`, `typecheck`, `lint`, `format:check`) gates green on `main` after closeout merge. Playwright suite green on the merged frontend.

**Reviewer's M2 quality-complete recommendation:** all blocking findings resolved.
```

- Closes issue #34 on merge.
- No code changes in this PR.

---

## 6. Test Strategy Summary

**Per CLAUDE.md TDD discipline:** every code-touching finding (F1–F5) follows Red → Green → Refactor with separate commits per phase.

**Backend tests:**
- F1 adds `tests/test_security_headers.py` (4 cases).
- F2 adds `tests/test_csrf_middleware.py` (6 cases).
- All backend tests use **real PostgreSQL via testcontainers** per `/web/CLAUDE.md`.

**Frontend tests:**
- F3 adds `src/lib/__tests__/api-client.refresh-coalescing.test.ts` (2 cases minimum: success-coalescing + failure-coalescing).
- F4 updates an existing `useRegister` test.
- F5 updates `WeightEntryTable.test.tsx` and adds a Playwright assertion.

**E2E:**
- Playwright runs locally for F1, F2, F3, F5 PRs.

**Coverage:** every PR must keep coverage thresholds green (no regression below current 90% backend / 97% frontend).

---

## 7. Documentation Deliverables

| PR | Document | Path |
|---|---|---|
| F1 | ADR-0016 — Security header policy (HSTS + CSP) | `docs/adr/0016-security-header-policy.md` |
| F2 | ADR-0017 — CSRF Origin/Referer validation | `docs/adr/0017-csrf-origin-referer-validation.md` |
| F3 | ADR-0018 — Concurrent refresh coalescing | `docs/adr/0018-concurrent-refresh-coalescing.md` |
| F5 | DDR-0004 — Weight table action button conversion | `docs/ddr/0004-weight-table-action-button-conversion.md` |
| Closeout | M2 quality doc resolution review | `docs/standards/M2_WEB_APP_QUALITY.md` (appended) |

Each ADR uses the template at `~/.claude/templates/ADR_TEMPLATE.md`. Each DDR uses the template at `~/.claude/templates/DDR_TEMPLATE.md` (or the existing DDR pattern under `docs/ddr/`).

---

## 8. Risks and Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| F2 middleware breaks Playwright by rejecting its Origin | Medium | Playwright spawns Chromium with `Origin: http://localhost:5173`, which is already in `cors_allowed_origins`. Run `npm run test:e2e` locally before pushing F2. |
| F1 strict CSP breaks Swagger UI in production | Low | Path-aware override on `/api/docs` and `/api/redoc` allows CDN. Test asserts override applies. |
| F3 promise-coalescing introduces a memory leak | Low | The `.finally()` clears `inflightRefresh` on every settle. Test asserts the promise is re-created for the second 401. |
| F5 visual change rejected at review | Low | DDR-0004 captures the design rationale and visual diff up front. |
| F6 surfaces more drift than expected | Low | Scope is "drift discovered during F1–F5"; bound the PR by treating anything outside the changed files as a follow-up. |
| Six PRs in flight cause merge conflicts | Low | Files are disjoint across findings. Recommended merge order is sequential but parallelism is safe. |
| Issue #34 task list lacks F6 checkbox | Certain | First execution action is to amend issue #34 to add F6. |

---

## 9. Execution Checklist

Run in order. Each checkbox must be verifiable.

**Pre-work**

- [ ] Amend issue #34 to add F6 task checkbox (see §2.3).
- [ ] Confirm `main` is up-to-date locally.

**PR 0 — docs baseline**

- [ ] `git checkout -b feature/m2-quality-review-doc` from `main`.
- [ ] Verify `docs/standards/M2_WEB_APP_QUALITY.md` is staged (it currently is).
- [ ] `git commit -m "docs: add M2 web app quality review (GH-34)"`.
- [ ] Push and open PR; merge to `main`.

**PR 1 — F1**

- [ ] Branch `feature/issue-34-F1-security-headers` from updated `main`.
- [ ] Red commit: failing security-headers test.
- [ ] Green commit: HSTS + CSP middleware change.
- [ ] (Optional) Refactor commit: extract constants.
- [ ] Docs commit: add ADR-0016.
- [ ] Full local backend + frontend gate green.
- [ ] PR opened referencing #34.

**PR 2 — F2**

- [ ] Branch `feature/issue-34-F2-csrf-origin-referer` from `main`.
- [ ] Red commit: failing CSRF tests.
- [ ] Green commit: CSRF middleware + registration in `main.py`.
- [ ] Docs commit: add ADR-0017.
- [ ] Playwright suite green locally.
- [ ] PR opened referencing #34.

**PR 3 — F3**

- [ ] Branch `feature/issue-34-F3-refresh-coalescing` from `main`.
- [ ] Red commit: failing concurrent-refresh tests.
- [ ] Green commit: shared `inflightRefresh` promise.
- [ ] Docs commit: add ADR-0018.
- [ ] PR opened referencing #34.

**PR 4 — F4**

- [ ] Branch `feature/issue-34-F4-generic-register-error` from `main`.
- [ ] Red commit: updated useRegister test expecting generic message.
- [ ] Green commit: useRegister hook update.
- [ ] PR opened referencing #34 and ADR-0010.

**PR 5 — F5**

- [ ] Branch `feature/issue-34-F5-action-target-size` from `main`.
- [ ] Red commit: failing component + Playwright target-size assertion.
- [ ] Green commit: `IconButton` → `Button` conversion.
- [ ] Docs commit: add DDR-0004.
- [ ] PR opened referencing #34.

**PR 6 — F6**

- [ ] Branch `feature/issue-34-F6-doc-drift-cleanup` from `main`.
- [ ] Audit grep complete; staleness inventory captured.
- [ ] Commit: doc/version drift updates.
- [ ] PR opened referencing #34.

**PR 7 — closeout**

- [ ] Branch `feature/issue-34-closeout` from `main` after F1–F6 merged.
- [ ] Append "Resolution Review" section to `M2_WEB_APP_QUALITY.md` with merge SHAs.
- [ ] PR opened; closes #34 on merge.

---

## 10. References

- Issue: [#34 — Remediate M2 Web App Quality Review blocking findings](https://github.com/rgoshen-snhu/WeightToGo/issues/34)
- Authoritative review: `docs/standards/M2_WEB_APP_QUALITY.md`
- SRS: `docs/specs/WeighToGo_Web_SRS_v2.md` — NFR-S-9, NFR-S-10, NFR-A-5, FR-A-1, FR-A-9
- ADR-0010 — Generic authentication error policy: `docs/adr/0010-generic-authentication-error-policy.md`
- ADR-0012 — Three-pattern backend architecture: `docs/adr/0012-three-pattern-backend-architecture.md`
- ADR-0013 — Refresh token rotation + family revocation: `docs/adr/0013-refresh-token-rotation-family-revocation.md`
- ADR-0014 — TanStack Query for server state: `docs/adr/0014-tanstack-query-for-server-state.md`
- CS 499 code review checklist: `docs/standards/cs499_code_review_checklist.md`
