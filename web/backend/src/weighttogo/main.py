"""FastAPI application for the Weigh to Go! backend.

Application entry point.  Mounts all domain routers under the /api/v1 prefix,
configures slowapi for rate limiting, and wires the shared logging setup.

Security headers and CORS middleware are applied here per SRS §NFR-S-8,
§NFR-S-10.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from weighttogo.achievements.interface.router import router as achievements_router
from weighttogo.auth.interface.router import limiter
from weighttogo.auth.interface.router import router as auth_router
from weighttogo.config import get_settings
from weighttogo.dashboard.interface.router import router as dashboard_router
from weighttogo.goals.interface.router import router as goals_router
from weighttogo.interface.middleware.csrf import CsrfOriginRefererMiddleware
from weighttogo.preferences.interface.router import router as preferences_router
from weighttogo.shared.error_handlers import validation_exception_handler
from weighttogo.shared.logging import configure_logging
from weighttogo.weight_tracking.interface.router import router as weight_router

configure_logging()

app = FastAPI(
    title="Weigh to Go! API",
    version="0.3.0",  # x-release-please-version
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/v1/openapi.json",
)

# ── RFC 7807 validation error handler (SRS §9.2) ─────────────────────────────

app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]

# ── Rate limiting ──────────────────────────────────────────────────────────────

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
app.add_middleware(SlowAPIMiddleware)

# ── CSRF Origin/Referer validation (SRS §NFR-S-9) ────────────────────────────
# Registered before CORSMiddleware so that Starlette's LIFO stack places CORS
# outermost — CORS handles OPTIONS preflights before CSRF evaluates the request.

app.add_middleware(CsrfOriginRefererMiddleware)

# ── CORS (SRS §NFR-S-8) ───────────────────────────────────────────────────────


def _get_cors_origins() -> list[str]:
    settings = get_settings()
    return [o.strip() for o in settings.cors_allowed_origins.split(",") if o.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Request-ID"],
)

# ── Security headers middleware (SRS §NFR-S-10) ───────────────────────────────

_DEFAULT_CSP = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
_DOCS_CSP = (
    "default-src 'self'; "
    "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
    "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
    "img-src 'self' data: https://fastapi.tiangolo.com; "
    "connect-src 'self'"
)
_DOCS_PATHS = frozenset({"/api/docs", "/api/redoc", "/api/v1/openapi.json"})
_HSTS_VALUE = "max-age=31536000; includeSubDomains"


@app.middleware("http")
async def add_security_headers(request: Request, call_next: object) -> object:
    """Add OWASP-recommended security headers to every response (SRS §NFR-S-10)."""
    from collections.abc import Awaitable, Callable

    from starlette.responses import Response

    next_fn: Callable[[Request], Awaitable[Response]] = call_next  # type: ignore[assignment]
    response: Response = await next_fn(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
    csp = _DOCS_CSP if request.url.path in _DOCS_PATHS else _DEFAULT_CSP
    response.headers["Content-Security-Policy"] = csp
    if get_settings().environment == "production":
        response.headers["Strict-Transport-Security"] = _HSTS_VALUE
    return response


# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth_router, prefix="/api/v1")
app.include_router(weight_router, prefix="/api/v1")
app.include_router(goals_router, prefix="/api/v1")
app.include_router(achievements_router, prefix="/api/v1")
app.include_router(preferences_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")


# ── Health check (SRS §NFR-O-3) ───────────────────────────────────────────────


@app.get("/health")
def health() -> dict[str, str]:
    """Report service liveness and the active environment."""
    return {"status": "ok", "environment": get_settings().environment}
