"""Weight tracking bounded context.

Manages the recording, retrieval, and history of user weight entries.
This context owns the WeightEntry aggregate and enforces the business rule
that entries are immutable once committed.
"""
