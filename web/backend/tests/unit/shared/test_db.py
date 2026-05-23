"""Unit tests for the get_db_session database session lifecycle."""

import contextlib
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

import weighttogo.shared.db as db_module
from weighttogo.shared.db import get_db_session


def test_db_session_commits_exactly_once_on_http_exception() -> None:
    """HTTPException path must commit exactly once — not twice (double-commit bug)."""
    mock_session = MagicMock()

    with (
        patch.object(db_module, "_engine", MagicMock()),
        patch.object(db_module, "_SessionLocal", MagicMock(return_value=mock_session)),
    ):
        gen = get_db_session()
        next(gen)
        with contextlib.suppress(HTTPException):
            gen.throw(HTTPException(status_code=401))

    assert mock_session.commit.call_count == 1
    mock_session.rollback.assert_not_called()
    mock_session.close.assert_called_once()


def test_db_session_commits_exactly_once_on_success() -> None:
    """Successful request path must commit exactly once."""
    mock_session = MagicMock()

    with (
        patch.object(db_module, "_engine", MagicMock()),
        patch.object(db_module, "_SessionLocal", MagicMock(return_value=mock_session)),
    ):
        gen = get_db_session()
        next(gen)
        with contextlib.suppress(StopIteration):
            next(gen)  # advance past yield → triggers commit then close

    assert mock_session.commit.call_count == 1
    mock_session.rollback.assert_not_called()
    mock_session.close.assert_called_once()


def test_db_session_rolls_back_on_unexpected_exception() -> None:
    """Unexpected exceptions must trigger rollback and no commit."""
    mock_session = MagicMock()

    with (
        patch.object(db_module, "_engine", MagicMock()),
        patch.object(db_module, "_SessionLocal", MagicMock(return_value=mock_session)),
    ):
        gen = get_db_session()
        next(gen)
        with contextlib.suppress(RuntimeError):
            gen.throw(RuntimeError("unexpected"))

    mock_session.rollback.assert_called_once()
    mock_session.commit.assert_not_called()
    mock_session.close.assert_called_once()
