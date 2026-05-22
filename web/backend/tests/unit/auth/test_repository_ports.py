"""Unit tests verifying the repository port interfaces are importable and properly typed.

These tests confirm the protocol structure rather than logic, ensuring
that the port definitions are well-formed and can be implemented.
"""

from weighttogo.auth.domain.ports import IRefreshTokenRepository, IUserRepository


def test_user_repository_port_is_importable() -> None:
    assert IUserRepository is not None


def test_refresh_token_repository_port_is_importable() -> None:
    assert IRefreshTokenRepository is not None


def test_user_repository_has_required_methods() -> None:
    required = {"save", "get_by_email", "get_by_id"}
    protocol_methods = {m for m in dir(IUserRepository) if not m.startswith("_")}
    assert required <= protocol_methods


def test_refresh_token_repository_has_required_methods() -> None:
    required = {"save", "get_by_hash", "revoke_family"}
    protocol_methods = {m for m in dir(IRefreshTokenRepository) if not m.startswith("_")}
    assert required <= protocol_methods
