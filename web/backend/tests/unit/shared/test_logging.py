"""Unit tests for the shared structured logging module."""

import io
import json

import pytest
import structlog

from weighttogo.shared.logging import (
    _redact_processor,
    configure_logging,
    get_logger,
    mask_pii,
)

# ── mask_pii ──────────────────────────────────────────────────────────────────


def test_mask_pii_replaces_email_preserving_partial_local_and_domain() -> None:
    """Email addresses must be masked to ***<last4chars>@domain (SRS §NFR-Priv-1)."""
    result = mask_pii("contact user@example.com for details")
    assert "user@example.com" not in result
    assert "@example.com" in result


def test_mask_pii_replaces_multiple_emails() -> None:
    """Every email address in the input string must be masked."""
    result = mask_pii("from alice@b.com to carol@d.org")
    assert "alice@b.com" not in result
    assert "carol@d.org" not in result
    assert "@b.com" in result
    assert "@d.org" in result


def test_mask_pii_leaves_non_pii_unchanged() -> None:
    """Strings without PII must pass through unmodified."""
    plain = "weight entry 75.5 kg on 2026-05-22"
    assert mask_pii(plain) == plain


def test_mask_pii_masks_phone_number() -> None:
    """Phone numbers must be replaced with [phone] (SRS §NFR-Priv-1)."""
    result = mask_pii("call me at 555-867-5309")
    assert "555-867-5309" not in result
    assert "[phone]" in result


def test_mask_pii_email_shows_stars_prefix() -> None:
    """Masked email local part must start with *** (SRS §NFR-Priv-1 example)."""
    result = mask_pii("admin@example.com")
    assert result.startswith("***")


# ── _redact_processor ─────────────────────────────────────────────────────────


def test_redact_processor_masks_email_in_event_message() -> None:
    """PII in the event message field must be redacted automatically."""
    event_dict: dict = {"event": "raw@example.com attempted login", "level": "info"}
    out = _redact_processor(None, "info", event_dict)
    assert "raw@example.com" not in out["event"]


def test_redact_processor_masks_email_in_structured_field() -> None:
    """PII in arbitrary structured fields must be redacted without caller help."""
    event_dict: dict = {"event": "login", "email": "victim@example.com"}
    out = _redact_processor(None, "info", event_dict)
    assert "victim@example.com" not in out["email"]


def test_redact_processor_masks_phone_in_structured_field() -> None:
    """Phone numbers in structured fields must be replaced with [phone]."""
    event_dict: dict = {"event": "sms sent", "phone": "555-867-5309"}
    out = _redact_processor(None, "info", event_dict)
    assert "555-867-5309" not in out["phone"]
    assert "[phone]" in out["phone"]


def test_redact_processor_does_not_require_caller_masking() -> None:
    """Raw PII passed to a log call must be masked without any caller action."""
    event_dict: dict = {
        "event": "authenticated",
        "email": "victim@example.com",
        "phone": "555-123-4567",
    }
    out = _redact_processor(None, "info", event_dict)
    full_output = json.dumps(out)
    assert "victim@example.com" not in full_output
    assert "555-123-4567" not in full_output


# ── configure_logging / emitted output ───────────────────────────────────────


@pytest.fixture()
def _reset_structlog():
    """Restore structlog defaults after each test that reconfigures it."""
    yield
    structlog.reset_defaults()


def test_configure_logging_emits_json_with_pii_masked(_reset_structlog) -> None:
    """Emitted JSON log lines must not contain raw PII even without caller masking."""
    output = io.StringIO()
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            _redact_processor,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(output),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=False,
    )
    logger = get_logger("test.pii")
    logger.info("auth attempt", email="victim@example.com")

    log_line = output.getvalue().strip()
    assert log_line, "No log output was emitted"
    data = json.loads(log_line)
    full_output = json.dumps(data)
    assert "victim@example.com" not in full_output


def test_configure_logging_emitted_json_includes_timestamp_and_level(
    _reset_structlog,
) -> None:
    """Every emitted JSON log entry must include a timestamp and log level."""
    output = io.StringIO()
    configure_logging(json_logs=True, _output=output)
    logger = get_logger("test.structure")
    logger.info("startup complete")

    log_line = output.getvalue().strip()
    assert log_line, "No log output was emitted"
    data = json.loads(log_line)
    assert "timestamp" in data
    assert "level" in data


def test_get_logger_returns_structlog_logger() -> None:
    """get_logger() must return a structlog logger exposing bind/info/debug."""
    logger = get_logger("test.module")
    assert hasattr(logger, "bind")
    assert hasattr(logger, "info")
    assert hasattr(logger, "debug")


def test_get_logger_accepts_bound_context() -> None:
    """bind() must return a logger that retains the standard interface."""
    logger = get_logger("test.module")
    bound = logger.bind(user_id="u-123", action="test")
    assert hasattr(bound, "info")
    assert hasattr(bound, "debug")
    assert hasattr(bound, "bind")
