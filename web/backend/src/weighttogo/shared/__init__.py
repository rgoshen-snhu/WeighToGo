"""Shared layer for cross-cutting concerns.

Provides utilities that are reused across bounded contexts: structured
logging configuration, PII masking, request ID middleware, and the
SQLAlchemy async engine and session factory. Nothing in the shared layer
may import from a bounded context.
"""
