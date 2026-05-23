"""Application configuration loaded from the environment.

All settings are sourced from environment variables (and an optional ``.env``
file for local development).  No field has a secret default — required fields
raise a ``ValidationError`` at startup rather than silently using a wrong value.
"""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration sourced from environment variables and a .env file.

    Attributes:
        environment: Active deployment environment.  Controls logging verbosity
            and renderer choice (JSON vs. console).
        database_url: Full SQLAlchemy-compatible PostgreSQL connection string.
            Required — no default.
        secret_key: HMAC-SHA-256 signing key for JWT tokens.  Must be at least
            32 characters of non-whitespace random material.  Required — no default.
            Stored as ``SecretStr`` so the value is never accidentally logged.
        access_token_expire_minutes: JWT access token lifetime in minutes
            (SRS §FR-A-2, §NFR-S-3).
        refresh_token_expire_days: Refresh token lifetime in days
            (SRS §FR-A-2).
        max_login_attempts: Consecutive failures before account lockout
            (SRS §NFR-S-6).
        lockout_duration_minutes: Initial lockout period in minutes; subsequent
            cycles apply exponential back-off capped at 24 hours (SRS §NFR-S-6).
        cors_allowed_origins: Comma-separated list of allowed CORS origins.
            Wildcards are never accepted (SRS §NFR-S-8).
        log_level: Minimum log severity passed to stdlib logging.
        cookie_secure: Whether auth cookies carry the ``Secure`` attribute.
            Derived from ``environment``: always ``True`` in production.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Core ──────────────────────────────────────────────────────────────────

    environment: Literal["development", "test", "production"] = "development"
    database_url: str  # required — no default

    # ── Auth (SRS §12.5.1) ────────────────────────────────────────────────────

    secret_key: SecretStr  # required — no default; must be ≥32 non-whitespace chars
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15

    # ── Security ──────────────────────────────────────────────────────────────

    cors_allowed_origins: str = "http://localhost:5173"  # override in prod
    jwt_issuer: str = "weighttogo-api"
    jwt_audience: str = "weighttogo-clients"
    # When True the rate limiter reads the rightmost IP in X-Forwarded-For
    # instead of REMOTE_ADDR. Only enable when a trusted reverse proxy is in
    # front of the API; never enable if clients can set this header directly.
    trusted_proxies: bool = False
    # Set RATE_LIMIT_ENABLED=false in E2E / dev environments to prevent the
    # per-IP bucket from blocking test traffic originating from a single host.
    # Must always be True in production.
    rate_limit_enabled: bool = True

    # ── Observability ─────────────────────────────────────────────────────────

    log_level: str = "INFO"

    # ── Derived properties ────────────────────────────────────────────────────

    @property
    def cookie_secure(self) -> bool:
        """Return True when cookies must carry the Secure attribute.

        Always True in production; False in development and test so that
        local HTTP development servers work without TLS.
        """
        return self.environment == "production"

    # ── Validators ────────────────────────────────────────────────────────────

    @field_validator("secret_key", mode="before")
    @classmethod
    def _validate_secret_key(cls, v: object) -> object:
        """Reject blank, whitespace-only, or too-short secret keys."""
        raw = v.get_secret_value() if isinstance(v, SecretStr) else str(v) if v is not None else ""
        stripped = raw.strip()
        if not stripped:
            raise ValueError("SECRET_KEY must not be blank or whitespace-only.")
        if len(stripped) < 32:
            raise ValueError(f"SECRET_KEY must be at least 32 characters; got {len(stripped)}.")
        return v


@lru_cache
def get_settings() -> Settings:
    """Return the application settings, constructed once and cached.

    Settings are built lazily rather than at import time so that a
    misconfigured environment surfaces where settings are first used,
    instead of crashing every module that imports this one.

    Returns:
        A fully-validated ``Settings`` instance.
    """
    return Settings()  # type: ignore[call-arg]  # pydantic-settings injects fields from env
