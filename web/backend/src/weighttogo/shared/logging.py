"""Structured logging setup for the Weigh to Go! backend.

Configures structlog centrally with:
- JSON rendering (stdout) or console rendering (dev)
- ISO timestamp and log level on every entry
- Automatic PII redaction for email and phone values (SRS §FR-A-10, §NFR-Priv-1)
- Request-ID propagation via contextvars

Usage::

    from weighttogo.shared.logging import configure_logging, get_logger

    configure_logging()          # call once at app startup
    logger = get_logger(__name__)
    logger.info("user action", user_id="u-123")  # raw PII is masked automatically
"""

import logging
import re
import sys
from typing import Any, TextIO

import structlog

_EMAIL_RE: re.Pattern[str] = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_PHONE_RE: re.Pattern[str] = re.compile(r"\b(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")


def _mask_email_in_string(value: str) -> str:
    """Mask each email address, preserving the last 4 chars of the local part and the domain.

    SRS §NFR-Priv-1 example: user@example.com → ***er@example.com
    """

    def _replace(m: re.Match[str]) -> str:
        local, domain = m.group(0).split("@", 1)
        # Show up to 4 trailing chars but always mask at least 1 char.
        # This matches the SRS §NFR-Priv-1 example: rick → ***ick.
        visible_count = min(len(local) - 1, 4)
        visible = local[-visible_count:] if visible_count > 0 else ""
        return f"***{visible}@{domain}"

    return _EMAIL_RE.sub(_replace, value)


def mask_pii(value: str) -> str:
    """Mask PII in *value*: email addresses and phone numbers.

    Email addresses are partially masked per SRS §NFR-Priv-1.
    Phone numbers are replaced with ``[phone]``.

    This function is also available as an explicit utility for callers who need
    to sanitise values before storing them outside of logs.

    Args:
        value: An arbitrary string that may contain PII.

    Returns:
        The input string with PII replaced by masked equivalents.
    """
    masked = _mask_email_in_string(value)
    return _PHONE_RE.sub("[phone]", masked)


def _redact_processor(
    logger: Any,
    method: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Structlog processor that redacts PII from every string value in the event dict.

    Runs unconditionally on every log call, so callers never need to call
    ``mask_pii()`` before logging.
    """
    for key in list(event_dict):
        value = event_dict[key]
        if isinstance(value, str):
            event_dict[key] = mask_pii(value)
    return event_dict


def configure_logging(
    *,
    json_logs: bool = True,
    level: int = logging.INFO,
    _output: TextIO | None = None,
) -> None:
    """Configure structlog for the application.

    Call once at application startup before any loggers are used. Sets up
    JSON or console rendering, ISO timestamps, log level, contextvars-based
    request-ID propagation, and automatic PII redaction.

    Args:
        json_logs: Emit JSON lines when ``True`` (production); use the
            coloured console renderer when ``False`` (local dev).
        level: Minimum stdlib log level to propagate.
        _output: Override output stream (used in tests only).
    """
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", key="timestamp"),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        _redact_processor,
    ]

    if json_logs:
        renderer: Any = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    output_stream = _output if _output is not None else sys.stdout

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(output_stream),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=output_stream,
        level=level,
        force=True,
    )


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """Return a bound structlog logger for *name*.

    Args:
        name: Logger name, typically ``__name__`` of the calling module.

    Returns:
        A structlog ``BoundLogger`` ready to emit structured log events.
    """
    return structlog.stdlib.get_logger(name)
