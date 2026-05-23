"""FastAPI router for the /api/v1/auth endpoints.

Implements the full authentication flow per SRS §9.3, §FR-A-1 through FR-A-5,
FR-A-9, FR-A-10, NFR-S-3, NFR-S-5, NFR-S-6, NFR-S-7.

Security decisions:
- Access token and refresh token are delivered as HTTP-only, SameSite=Strict cookies.
- All auth failure paths return the same generic 401 body to prevent user enumeration.
- Rate limiting applied to /register (3/hour), /login and /refresh (10/min) via slowapi.
- Account lockout is handled by the domain use case.
- PII is never logged in plain text (structlog processor handles masking).

Cookie names:
    ``access_token``  — JWT access token (15 min TTL)
    ``refresh_token`` — Opaque refresh token (7 day TTL)
"""

from __future__ import annotations

import contextlib
from collections.abc import Callable

import structlog
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from weighttogo.auth.application.authenticate_user import AuthenticateUser, AuthenticateUserCommand
from weighttogo.auth.application.issue_tokens import IssueTokens, IssueTokensCommand
from weighttogo.auth.application.refresh_session import RefreshSession, RefreshSessionCommand
from weighttogo.auth.application.register_user import RegisterUser, RegisterUserCommand
from weighttogo.auth.application.revoke_session import RevokeSession, RevokeSessionCommand
from weighttogo.auth.domain.exceptions import (
    AccountLockedError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)
from weighttogo.auth.infrastructure.jwt_adapter import (
    InvalidTokenError,
    JwtAdapter,
    TokenExpiredError,
)
from weighttogo.auth.infrastructure.password import BcryptPasswordAdapter
from weighttogo.auth.infrastructure.repositories import (
    SqlAlchemyRefreshTokenRepository,
    SqlAlchemyUserRepository,
)
from weighttogo.auth.interface.schemas import LoginRequest, RegisterRequest, UserResponse
from weighttogo.config import get_settings
from weighttogo.shared.db import get_db_session

logger = structlog.stdlib.get_logger(__name__)


def _make_rate_limit_key(settings: object) -> Callable[[Request], str]:
    """Return a slowapi key_func that respects the ``trusted_proxies`` setting.

    When ``trusted_proxies`` is *True* the key is the rightmost IP in
    ``X-Forwarded-For`` (the last untrusted hop before the proxy).  When
    *False* (the safe default) ``REMOTE_ADDR`` is used so a spoofed XFF
    header cannot let an attacker reset their own rate-limit bucket.

    Args:
        settings: The application ``Settings`` instance.

    Returns:
        A callable ``(request) -> str`` suitable as a slowapi ``key_func``.
    """
    from weighttogo.config import Settings

    s = settings if isinstance(settings, Settings) else get_settings()

    def key_func(request: Request) -> str:
        if s.trusted_proxies:
            xff = request.headers.get("x-forwarded-for", "")
            if xff:
                # The rightmost address is the last proxy-added hop — use it.
                return xff.split(",")[-1].strip()
        return get_remote_address(request)

    return key_func


# Rate limiter instance — shared via the app.state.limiter pattern.
# Disabled when RATE_LIMIT_ENABLED=false (e.g. E2E test runs) so that
# per-IP buckets do not block a test suite where all traffic shares one host.
_settings = get_settings()
limiter = Limiter(key_func=_make_rate_limit_key(_settings), enabled=_settings.rate_limit_enabled)

router = APIRouter(prefix="/auth", tags=["auth"])

# Cookie configuration (SRS §NFR-S-3)
_ACCESS_COOKIE = "access_token"
_REFRESH_COOKIE = "refresh_token"

# Generic error body — identical for all auth failures (SRS §FR-A-9, §NFR-S-7)
_GENERIC_AUTH_ERROR = {"detail": "Invalid credentials."}


# ── Dependency factories ───────────────────────────────────────────────────────


def _get_jwt_adapter() -> JwtAdapter:
    """Return a JwtAdapter configured from settings."""
    settings = get_settings()
    return JwtAdapter(
        secret_key=settings.secret_key.get_secret_value(),
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
    )


def _get_password_adapter() -> BcryptPasswordAdapter:
    return BcryptPasswordAdapter()


def get_current_user_id(
    request: Request,
    jwt_adapter: JwtAdapter = Depends(_get_jwt_adapter),
) -> int:
    """FastAPI dependency: extract and verify the access token from the cookie.

    Args:
        request: The incoming HTTP request.
        jwt_adapter: The JWT verification adapter.

    Returns:
        The authenticated user's surrogate ID.

    Raises:
        HTTPException: 401 when the token is missing, expired, or invalid.
    """
    token = request.cookies.get(_ACCESS_COOKIE)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")
    try:
        user_id = jwt_adapter.verify_access_token(token)
    except (TokenExpiredError, InvalidTokenError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated."
        ) from exc
    return user_id


def _set_auth_cookies(
    response: Response,
    access_token: str,
    raw_refresh: str,
    settings: object,
) -> None:
    """Write access and refresh token cookies onto *response*."""
    from weighttogo.config import Settings

    s = settings if isinstance(settings, Settings) else get_settings()
    base_kwargs = {
        "httponly": True,
        "samesite": "strict",
        "secure": s.cookie_secure,
    }
    response.set_cookie(
        key=_ACCESS_COOKIE,
        value=access_token,
        max_age=s.access_token_expire_minutes * 60,
        path="/",
        **base_kwargs,  # type: ignore[arg-type]
    )
    # Scope the refresh token to auth endpoints only so it is not sent on
    # every API request (e.g. weight entries, goals) — principle of least exposure.
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=raw_refresh,
        max_age=s.refresh_token_expire_days * 24 * 60 * 60,
        path="/api/v1/auth",
        **base_kwargs,  # type: ignore[arg-type]
    )


def _clear_auth_cookies(response: Response) -> None:
    """Delete access and refresh token cookies from the client.

    Attributes must match what ``_set_auth_cookies`` used; browsers only
    delete a cookie when the deletion Set-Cookie header carries the same
    ``Path``, ``Secure``, ``SameSite``, and ``HttpOnly`` attributes.
    """
    s = get_settings()
    delete_kwargs = {
        "httponly": True,
        "samesite": "strict",
        "secure": s.cookie_secure,
    }
    response.delete_cookie(key=_ACCESS_COOKIE, path="/", **delete_kwargs)  # type: ignore[arg-type]
    response.delete_cookie(key=_REFRESH_COOKIE, path="/api/v1/auth", **delete_kwargs)  # type: ignore[arg-type]


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    summary="Register a new user account (FR-A-1)",
)
@limiter.limit("3/hour")
def register(
    request: Request,
    payload: RegisterRequest,
    response: Response,
    session: Session = Depends(get_db_session),
    password_adapter: BcryptPasswordAdapter = Depends(_get_password_adapter),
    jwt_adapter: JwtAdapter = Depends(_get_jwt_adapter),
) -> UserResponse:
    """Create a new user account and return a session cookie.

    Args:
        request: The incoming HTTP request (required by slowapi).
        payload: Validated registration fields.
        response: The outgoing HTTP response (used to set cookies).
        session: The active database session.
        password_adapter: Bcrypt password hashing adapter.
        jwt_adapter: JWT issuance adapter.

    Returns:
        The newly created user's public data.

    Raises:
        HTTPException: 409 when the email is already registered (generic message).
        HTTPException: 422 when validation fails.
    """
    settings = get_settings()
    user_repo = SqlAlchemyUserRepository(session)
    token_repo = SqlAlchemyRefreshTokenRepository(session)

    register_uc = RegisterUser(user_repo=user_repo, password_adapter=password_adapter)
    issue_uc = IssueTokens(
        jwt_adapter=jwt_adapter,
        token_repo=token_repo,
        refresh_ttl_days=settings.refresh_token_expire_days,
        access_ttl_minutes=settings.access_token_expire_minutes,
    )

    try:
        user = register_uc.execute(
            RegisterUserCommand(
                email=str(payload.email),
                password=payload.password,
                display_name=payload.display_name,
            )
        )
    except EmailAlreadyRegisteredError as exc:
        # Generic 409 — must not confirm whether the email exists (SRS §FR-A-1)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The request could not be completed.",
        ) from exc

    assert user.user_id is not None
    tokens = issue_uc.execute(IssueTokensCommand(user_id=user.user_id))
    _set_auth_cookies(response, tokens.access_token, tokens.raw_refresh_token, settings)

    logger.info("user_registered", user_id=user.user_id)
    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        display_name=user.display_name,
        created_at=user.created_at,
    )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    summary="Authenticate and receive session cookies (FR-A-2)",
)
@limiter.limit("10/minute")
def login(
    request: Request,
    payload: LoginRequest,
    response: Response,
    session: Session = Depends(get_db_session),
    password_adapter: BcryptPasswordAdapter = Depends(_get_password_adapter),
    jwt_adapter: JwtAdapter = Depends(_get_jwt_adapter),
) -> UserResponse:
    """Verify credentials and issue session cookies.

    Args:
        request: The incoming HTTP request (required by slowapi).
        payload: Validated login fields.
        response: The outgoing HTTP response (used to set cookies).
        session: The active database session.
        password_adapter: Bcrypt verification adapter.
        jwt_adapter: JWT issuance adapter.

    Returns:
        The authenticated user's public data.

    Raises:
        HTTPException: 401 for any credential failure (generic message).
        HTTPException: 423 when the account is locked.
    """
    settings = get_settings()
    user_repo = SqlAlchemyUserRepository(session)
    token_repo = SqlAlchemyRefreshTokenRepository(session)

    auth_uc = AuthenticateUser(
        user_repo=user_repo,
        password_adapter=password_adapter,
        max_attempts=settings.max_login_attempts,
        lockout_minutes=settings.lockout_duration_minutes,
    )
    issue_uc = IssueTokens(
        jwt_adapter=jwt_adapter,
        token_repo=token_repo,
        refresh_ttl_days=settings.refresh_token_expire_days,
        access_ttl_minutes=settings.access_token_expire_minutes,
    )

    try:
        user = auth_uc.execute(
            AuthenticateUserCommand(email=str(payload.email), password=payload.password)
        )
    except AccountLockedError as exc:
        logger.warning("account_locked", locked_until=str(exc.locked_until))
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is temporarily locked. Please try again later.",
        ) from exc
    except InvalidCredentialsError as exc:
        logger.info("login_failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_GENERIC_AUTH_ERROR["detail"],
        ) from exc

    assert user.user_id is not None
    tokens = issue_uc.execute(IssueTokensCommand(user_id=user.user_id))
    _set_auth_cookies(response, tokens.access_token, tokens.raw_refresh_token, settings)

    logger.info("user_logged_in", user_id=user.user_id)
    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        display_name=user.display_name,
        created_at=user.created_at,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="End the current session (FR-A-3)",
)
@limiter.limit("10/minute")
def logout(
    request: Request,
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=_REFRESH_COOKIE),
    session: Session = Depends(get_db_session),
    jwt_adapter: JwtAdapter = Depends(_get_jwt_adapter),
) -> None:
    """Revoke the refresh token family and clear session cookies.

    Does not require a valid access token — clients must be able to log out
    even after the 15-minute access token has expired.  Auth cookies are always
    cleared regardless of token state.

    Args:
        request: The incoming HTTP request (required by slowapi rate limiting).
        response: The outgoing HTTP response (used to clear cookies).
        refresh_token: The refresh token from the cookie (optional).
        session: The active database session.
        jwt_adapter: JWT adapter used for token hashing.
    """
    if refresh_token is not None:
        token_repo = SqlAlchemyRefreshTokenRepository(session)
        revoke_uc = RevokeSession(token_repo=token_repo, jwt_adapter=jwt_adapter)
        with contextlib.suppress(InvalidCredentialsError):
            revoke_uc.execute(RevokeSessionCommand(raw_refresh_token=refresh_token))

    _clear_auth_cookies(response)
    logger.info("user_logged_out")


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    summary="Rotate the refresh token and issue a new access token (FR-A-4)",
)
@limiter.limit("5/minute")
def refresh(
    request: Request,
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=_REFRESH_COOKIE),
    session: Session = Depends(get_db_session),
    jwt_adapter: JwtAdapter = Depends(_get_jwt_adapter),
) -> UserResponse:
    """Rotate the refresh token.

    Args:
        request: The incoming HTTP request (required by slowapi).
        response: The outgoing HTTP response (used to set cookies).
        refresh_token: The current refresh token from the cookie.
        session: The active database session.
        jwt_adapter: JWT issuance adapter.

    Returns:
        The user's public data with refreshed cookies.

    Raises:
        HTTPException: 401 when no valid refresh token is present.
    """
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_GENERIC_AUTH_ERROR["detail"],
        )

    settings = get_settings()
    user_repo = SqlAlchemyUserRepository(session)
    token_repo = SqlAlchemyRefreshTokenRepository(session)

    refresh_uc = RefreshSession(
        jwt_adapter=jwt_adapter,
        token_repo=token_repo,
        refresh_ttl_days=settings.refresh_token_expire_days,
        access_ttl_minutes=settings.access_token_expire_minutes,
    )

    try:
        tokens = refresh_uc.execute(RefreshSessionCommand(raw_refresh_token=refresh_token))
    except InvalidCredentialsError as exc:
        _clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_GENERIC_AUTH_ERROR["detail"],
        ) from exc

    # Look up the user and verify they are still active
    new_user_id = jwt_adapter.verify_access_token(tokens.access_token)
    user = user_repo.get_by_id(new_user_id)
    if user is None or not user.is_active:
        # Deleted or deactivated account — revoke the whole token family and deny access.
        # The old token is already revoked; look it up by hash to get family_id.
        old_token = token_repo.get_by_hash(jwt_adapter.hash_token(refresh_token))
        if old_token is not None:
            token_repo.revoke_family(old_token.family_id)
        _clear_auth_cookies(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    _set_auth_cookies(response, tokens.access_token, tokens.raw_refresh_token, settings)
    return UserResponse(
        user_id=user.user_id,  # type: ignore[arg-type]
        email=user.email,
        display_name=user.display_name,
        created_at=user.created_at,
    )


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    summary="Return the current user's identity (FR-A-5)",
)
def me(
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
) -> UserResponse:
    """Return the current authenticated user's public data.

    Args:
        session: The active database session.
        current_user_id: The authenticated user's ID from the access token.

    Returns:
        The current user's public identity.

    Raises:
        HTTPException: 401 when no valid access token is present.
    """
    user_repo = SqlAlchemyUserRepository(session)
    user = user_repo.get_by_id(current_user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    return UserResponse(
        user_id=user.user_id,  # type: ignore[arg-type]
        email=user.email,
        display_name=user.display_name,
        created_at=user.created_at,
    )
