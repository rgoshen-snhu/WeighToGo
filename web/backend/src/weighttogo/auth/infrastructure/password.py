"""Bcrypt password hashing adapter.

Implements the password-hashing port using the ``bcrypt`` library directly
with a cost factor of 12 (SRS §NFR-S-2, §4.3.2).

Plain-text passwords are never logged, stored, or passed beyond this module.
Constant-time verification is provided by ``bcrypt.checkpw``, which prevents
timing-based side-channel attacks.
"""

import bcrypt as _bcrypt


class BcryptPasswordAdapter:
    """Adapter for the password-hashing port backed by bcrypt (cost factor 12).

    This is the sole location in the codebase that touches ``bcrypt`` directly.
    Use cases receive this adapter through dependency injection, keeping the
    domain and application layers decoupled from the hashing implementation.
    """

    _ROUNDS: int = 12

    def hash(self, plaintext: str) -> str:
        """Hash *plaintext* with bcrypt and return the hash string.

        A new random salt is generated for every call, so two hashes of the
        same password will always differ.

        Args:
            plaintext: The raw password string supplied by the user.

        Returns:
            A bcrypt hash string in ``$2b$...`` format.
        """
        salt = _bcrypt.gensalt(rounds=self._ROUNDS)
        hashed = _bcrypt.hashpw(plaintext.encode(), salt)
        return hashed.decode()

    def verify(self, plaintext: str, hashed: str) -> bool:
        """Return ``True`` if *plaintext* matches *hashed* using constant-time comparison.

        Args:
            plaintext: The raw password string to check.
            hashed: A previously returned bcrypt hash string.

        Returns:
            ``True`` when the password is correct; ``False`` otherwise.
        """
        return bool(_bcrypt.checkpw(plaintext.encode(), hashed.encode()))
