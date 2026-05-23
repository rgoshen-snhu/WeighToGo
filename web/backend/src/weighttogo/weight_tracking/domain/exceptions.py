"""Domain exceptions for the weight_tracking bounded context.

Raised by use cases; caught and translated to HTTP responses by the
interface layer.  No framework dependencies.
"""

from __future__ import annotations


class WeightEntryNotFoundError(Exception):
    """Raised when a weight entry does not exist or belongs to another user.

    Maps to HTTP 404.
    """


class DuplicateObservationDateError(Exception):
    """Raised when a create or update would produce two active entries on the same date.

    Maps to HTTP 409.
    """


class ObservationDateInFutureError(Exception):
    """Raised when the observation_date is in the future.

    Maps to HTTP 422.
    """
