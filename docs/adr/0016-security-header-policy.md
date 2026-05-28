# ADR-0016: Security Header Policy (HSTS + CSP)

- **Date**: 2026-05-27
- **Status**: Accepted

## Context

The M2 Web App Quality Review (2026-05-23) identified a gap against SRS §NFR-S-10: the backend security-headers middleware emitted four of the six SRS-required headers (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`) but omitted `Strict-Transport-Security` (HSTS) and `Content-Security-Policy` (CSP). Both omissions are blocking findings requiring remediation before M2 quality sign-off.

Constraints relevant to the decision:

- The backend is a FastAPI JSON API. The only HTML-bearing endpoints are the auto-generated Swagger UI (`/api/docs`) and ReDoc (`/api/redoc`) pages, which load CDN assets from `cdn.jsdelivr.net` and `fastapi.tiangolo.com`.
- HSTS must not be sent over plain HTTP (development and test environments use HTTP); sending it would break local developer workflows.
- The existing `cookie_secure` setting in `config.py` is already environment-derived (`production` → True); HSTS follows the same pattern for consistency.

## Decision

**HSTS:** Emit `Strict-Transport-Security: max-age=31536000; includeSubDomains` only when `settings.environment == "production"`. Omit the header in `development` and `test`.

**CSP:** Emit a path-aware `Content-Security-Policy` on every response:

| Path | Policy |
|------|--------|
| `/api/docs`, `/api/redoc`, `/api/v1/openapi.json` | `default-src 'self'; script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; img-src 'self' data: https://fastapi.tiangolo.com; connect-src 'self'` |
| All other paths | `default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'` |

The default policy (`default-src 'none'`) is maximally restrictive. For a JSON API, HTML content never reaches the browser from production endpoints, so this policy provides defense-in-depth at zero functional cost. The docs-path override is the minimal relaxation required for the OpenAPI UI libraries to load their assets.

Constants are defined at module level in `main.py` (`_DEFAULT_CSP`, `_DOCS_CSP`, `_DOCS_PATHS`, `_HSTS_VALUE`) to keep the middleware body readable.

## Rationale

**Why environment-gated HSTS instead of always emitting it?**
HSTS over HTTP is ignored by browsers but confusing in log output and misleading in test assertions. The existing `cookie_secure` property uses the same pattern. Cross-environment consistency in the settings model outweighs the marginal benefit of emitting a no-op header in development.

**Why `'unsafe-inline'` in `script-src` for docs paths?**
FastAPI's `get_swagger_ui_html` generates a dynamic inline `<script>` block that initialises `SwaggerUIBundle`. Because the script content is parameterised at runtime (`openapi_url`, `swagger_ui_parameters`), a static SHA256 hash is impractical. A per-request nonce would require intercepting and rewriting the response body, which is disproportionate complexity for a developer tooling endpoint. `'unsafe-inline'` on the docs path only is the minimal correct allowance — it is consistent with the existing `'unsafe-inline'` already required for `style-src` (Swagger UI's CSS also uses inline styles), and the risk profile of a developer documentation page is substantially lower than a user-facing endpoint.

**Why a path-aware CSP instead of a uniform permissive policy?**
A uniform permissive CSP (e.g., `default-src 'self'`) would allow all same-origin resources. Since none of the JSON API endpoints serve HTML, the strict `default-src 'none'` policy is both correct and more protective. Restricting the relaxed policy to only the docs paths limits the attack surface: if an endpoint unexpectedly begins returning HTML content, it inherits the strict policy rather than the permissive one.

**Why not a production-only CSP?**
Enforcing CSP only in production creates a drift risk where staging or development tests would not catch CSP-breaking changes. Emitting CSP unconditionally keeps all environments consistent.

## Consequences

- **Positive**: Full SRS NFR-S-10 compliance (all six required headers). Docs endpoints continue to render correctly. HSTS policy (1-year max-age with subdomains) is industry-standard. Maximally strict default CSP provides defense-in-depth for future accidental HTML responses.
- **Negative**: Five lines of path-branching logic in the middleware. The HSTS production-environment test requires LRU-cache invalidation (`get_settings.cache_clear()`) which adds minor test complexity.
- **Follow-ups**: ADR-0017 (CSRF Origin/Referer validation) addresses the remaining SRS §NFR-S-9 gap identified in the same quality review.

## Alternatives Considered

- **Always emit HSTS** — rejected because sending HSTS over HTTP (development/test) would break local developer workflows without security benefit.
- **Uniform permissive CSP (`default-src 'self'`)** — rejected because the permissive policy affords no protection for the JSON API endpoints that constitute the bulk of traffic, and creates a wider surface for future HTML-injection risks.
- **Production-only CSP** — rejected because it would allow CSP-breaking changes to pass undetected in test environments.
- **Extract constants to a separate `security_headers.py` module** — deferred; the middleware body remains under 30 lines so the inline constants do not reduce readability. Can be revisited if additional headers or path categories are added.
