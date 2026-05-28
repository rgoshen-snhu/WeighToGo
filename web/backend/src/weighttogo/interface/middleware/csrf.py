"""CSRF Origin/Referer validation middleware (SRS §NFR-S-9, ADR-0017).

Rejects state-changing requests whose Origin or Referer header does not match
an allowed CORS origin.  Safe methods (GET, HEAD, OPTIONS) are always permitted.
"""

from urllib.parse import urlparse

from starlette.middleware.base import BaseHTTPMiddleware
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


def _allowed_origins() -> frozenset[str]:
    raw = get_settings().cors_allowed_origins
    return frozenset(o.strip() for o in raw.split(",") if o.strip())


def _origin_from_referer(referer: str) -> str:
    parsed = urlparse(referer)
    return f"{parsed.scheme}://{parsed.netloc}"


class CsrfOriginRefererMiddleware(BaseHTTPMiddleware):
    """Validate Origin/Referer on state-changing requests (ADR-0017)."""

    async def dispatch(self, request: Request, call_next: object) -> Response:
        """Enforce Origin/Referer validation on unsafe HTTP methods."""
        from collections.abc import Awaitable, Callable

        next_fn: Callable[[Request], Awaitable[Response]] = call_next  # type: ignore[assignment]

        if request.method in _SAFE_METHODS:
            return await next_fn(request)

        allowed = _allowed_origins()
        origin = request.headers.get("origin")
        referer = request.headers.get("referer")

        if origin:
            candidate = origin
        elif referer:
            candidate = _origin_from_referer(referer)
        else:
            candidate = None

        if candidate is None or candidate not in allowed:
            return JSONResponse(
                status_code=403,
                content=_FORBIDDEN_BODY,
                media_type="application/problem+json",
            )

        return await next_fn(request)
