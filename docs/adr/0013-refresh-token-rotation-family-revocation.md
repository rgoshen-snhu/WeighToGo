# ADR-0013: Refresh Token Rotation with Family-Based Revocation

- **Date**: 2026-05-22
- **Status**: Accepted

## Context

The web rebuild uses JWT access tokens delivered in HTTP-only cookies. JWTs are
stateless and cannot be individually invalidated before their expiry — a revoked
JWT is still cryptographically valid until its `exp` claim passes. To allow
session termination (logout, deactivation, theft response) before the access
token expires, the system needs a server-side session mechanism.

Refresh tokens serve as that mechanism: they are opaque, server-side-validated
credentials that the client exchanges for a new access token when the current
one expires. The design decisions are:

1. How long should a refresh token live?
2. Should presenting a refresh token consume it (rotation) or leave it reusable?
3. What happens when a refresh token that has already been used is presented
   again (replay)?

## Decision

**Rotation on every use.** Every successful call to `POST /auth/refresh` revokes
the presented token and issues a replacement. A valid token can be used exactly
once.

**Family-based replay detection.** All tokens issued within a single login
session share a `family_id` UUID. When a token is presented that has already
been revoked (`revoked_at IS NOT NULL`), the entire family is revoked immediately
and the request is rejected. This is the "token theft detection" signal: if a
revoked token is presented, either the legitimate client and an attacker both
have the token, or the attacker captured a token before the legitimate client
rotated it. In either case, terminating the family is the safe response.

**`replaced_by` tracking.** Each revoked token records the hash of its
successor, enabling audit of the rotation chain.

**Atomic rotation.** The read-check-revoke-insert sequence uses a row-level
`SELECT FOR UPDATE` lock on the token row in PostgreSQL so that two concurrent
requests cannot both observe the token as valid before either write commits.

**TTL.** Refresh tokens expire after 7 days by default (configurable via
`REFRESH_TOKEN_EXPIRE_DAYS`). Access tokens expire after 15 minutes
(configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).

Only the SHA-256 hash of each token is stored in the database. The raw token
value is delivered to the client once and never stored server-side.

## Rationale

- **Non-rotating refresh tokens** allow a stolen token to be used indefinitely
  until TTL expiry. With a 7-day TTL, a stolen token is a 7-day window of
  unauthorised access with no detection mechanism.
- **Rotation without family tracking** limits each stolen-token window to one
  use but provides no signal that theft has occurred. The attacker and the
  legitimate client both get one valid rotation; the system cannot distinguish
  which is the attacker.
- **Family-based revocation** closes that gap. When a used token is presented,
  the server knows both the legitimate client and a potential attacker have a
  copy of a token. Revoking the family forces re-authentication and terminates
  the attacker's access as soon as the detection event occurs.
- **Hashing in the database** limits the blast radius of a database breach.
  Raw tokens in the database would immediately yield valid session credentials
  for every active user.
- **`SELECT FOR UPDATE`** prevents the TOCTOU race where two concurrent refresh
  requests both observe the token as valid before either write lands. Without
  the lock, both requests could receive active successor tokens from the same
  parent, weakening the single-use guarantee.

## Alternatives Considered

- **Long-lived non-rotating refresh tokens** — Simple to implement. Rejected
  because a stolen token is valid for its full TTL with no detection or
  mitigation path.
- **Sliding-window expiry without rotation** — Extends the token's TTL on each
  use. Rejected because it keeps a stolen token valid as long as the attacker
  continues to use it, which is an indefinite window under continuous attack.
- **Opaque tokens without family tracking** — Rotation without family
  invalidation. Rejected because it detects nothing — a replay after rotation
  returns 401, but the family is still active, giving the attacker a separate
  active session from any token they captured before the last rotation.
- **JWT refresh tokens (stateless)** — No server-side state. Rejected because
  revocation requires server-side storage regardless — without it, logout cannot
  terminate the session before the token expires.

## Consequences

- **Positive**: Stolen tokens are detectable within one rotation window. Logout
  terminates the session immediately. Account deactivation terminates all active
  sessions. The database does not store raw token values.
- **Negative**: Every refresh operation requires a database write (revoke old,
  insert new). Concurrent refresh requests require row-level locking, which adds
  latency on high-contention sessions.
- **Edge case**: If the client successfully rotates a token but does not receive
  the response (network failure), the old token is revoked and the new token is
  lost. The client must re-authenticate. This is the standard trade-off for
  rotation; the alternative (keeping the old token valid) is worse.
- **Follow-ups**: A client-side retry strategy for the "lost rotation" case
  should be documented in the frontend ADR for the auth flow.

## References

- SRS §6 FR-A-9 (refresh token rotation requirement).
- SRS §7 NFR-S-3 (JWT and cookie security requirements).
- IETF RFC 6749 §10.4 (refresh token security considerations).
- OWASP Session Management Cheat Sheet.
- Implementation: `web/backend/src/weighttogo/auth/application/refresh_session.py`.

## Related ADRs

- **ADR-0009** — Email as Primary Identifier: the session belongs to a user
  identified by email; revocation terminates access for that identity.
- **ADR-0012** — Three-Pattern Backend Architecture: the `RefreshSession` use
  case, repository port, and SQLAlchemy adapter are split across the
  application, domain, and infrastructure layers per this architecture.

---

**Last Updated**: 2026-05-22
**Author**: Rick Goshen
**Approved By**: Technical Lead
