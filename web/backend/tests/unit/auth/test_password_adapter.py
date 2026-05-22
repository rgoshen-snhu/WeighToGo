"""Unit tests for the bcrypt password adapter."""

from weighttogo.auth.infrastructure.password import BcryptPasswordAdapter


def test_hash_returns_bcrypt_hash_string() -> None:
    adapter = BcryptPasswordAdapter()
    hashed = adapter.hash("MySecureP@ss1")
    assert hashed.startswith("$2b$")


def test_verify_returns_true_for_correct_password() -> None:
    adapter = BcryptPasswordAdapter()
    hashed = adapter.hash("MySecureP@ss1")
    assert adapter.verify("MySecureP@ss1", hashed) is True


def test_verify_returns_false_for_wrong_password() -> None:
    adapter = BcryptPasswordAdapter()
    hashed = adapter.hash("MySecureP@ss1")
    assert adapter.verify("WrongPassword!", hashed) is False


def test_two_hashes_of_same_password_are_different() -> None:
    """Each hash uses a new random salt."""
    adapter = BcryptPasswordAdapter()
    h1 = adapter.hash("SamePassword1!")
    h2 = adapter.hash("SamePassword1!")
    assert h1 != h2


def test_hash_uses_cost_factor_12_or_higher() -> None:
    adapter = BcryptPasswordAdapter()
    hashed = adapter.hash("AnyPassword1!")
    # bcrypt hash format: $2b$<rounds>$...
    rounds = int(hashed.split("$")[2])
    assert rounds >= 12
