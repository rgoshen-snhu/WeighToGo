"""CSRF Origin/Referer validation middleware (SRS §NFR-S-9, ADR-0017).

Rejects state-changing requests whose Origin or Referer header does not match
an allowed CORS origin or the API's own origin.  Safe methods (GET, HEAD,
OPTIONS) are always permitted.
"""

from urllib.parse import urlparse

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from weighttogo.config import get_settings

_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})

_FORBIDDEN_BODY = {
    "type": "about:blank",
    "title": "Forbidden",
    "status": 403,
    "detail": "Origin or Referer required and must match an allowed origin.",
}


def _normalize_origin(value: str) -> str:
    """Return a lowercase scheme://host[:port] string, or '' for invalid input.

    Normalises trailing slashes and mixed-case scheme/host so set lookups are
    reliable regardless of how the operator or a proxy serialised the value.
    Per RFC 6454 §6.1 the scheme and host components are case-insensitive.
    """
    parsed = urlparse(value.strip().rstrip("/"))
    if not parsed.scheme or not parsed.netloc:
        return ""
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}"


def _allowed_origins() -> frozenset[str]:
    """Return the set of normalised origins from cors_allowed_origins."""
    raw = get_settings().cors_allowed_origins
    return frozenset(n for o in raw.split(",") if (n := _normalize_origin(o)) != "")


def _origin_from_referer(referer: str) -> str:
    """Extract and normalise the origin portion of a Referer URL."""
    parsed = urlparse(referer)
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}"


def _request_own_origin(request: Request) -> str:
    """Return the normalised origin of the API server itself.

    Same-origin requests (e.g. Swagger UI at /api/docs posting back to the
    same host) are never CSRF attacks and must always be permitted.

    Note: behind a TLS-terminating reverse proxy, ``request.url.scheme`` may
    be ``http`` even when the public URL uses ``https``.  To make this work in
    production, launch uvicorn with ``--proxy-headers
    --forwarded-allow-ips=<proxy-ip>`` so Starlette honours
    ``X-Forwarded-Proto``.  See ADR-0017 for details.
    """
    return f"{request.url.scheme.lower()}://{request.url.netloc.lower()}"


class CsrfOriginRefererMiddleware(BaseHTTPMiddleware):
    """Validate Origin/Referer on state-changing requests (ADR-0017)."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Enforce Origin/Referer validation on unsafe HTTP methods."""
        if request.method in _SAFE_METHODS:
            return await call_next(request)

        # Allow the API's own origin so same-origin flows (e.g. Swagger UI)
        # are never blocked, in addition to configured CORS origins.
        allowed = _allowed_origins() | {_request_own_origin(request)}
        origin = request.headers.get("origin")
        referer = request.headers.get("referer")

        if origin:
            candidate = _normalize_origin(origin)
        elif referer:
            candidate = _origin_from_referer(referer)
        else:
            candidate = None

        # Only reject when a header is present and points to a disallowed origin.
        # If neither Origin nor Referer is sent (e.g. same-origin requests via a
        # reverse proxy such as Vite dev server with changeOrigin=true), the
        # request cannot be a browser-initiated CSRF attack — SameSite=Strict
        # cookies already prevent cross-site cookie submission in that path.
        if candidate is not None and candidate not in allowed:
            return JSONResponse(
                status_code=403,
                content=_FORBIDDEN_BODY,
                media_type="application/problem+json",
            )

        return await call_next(request)
