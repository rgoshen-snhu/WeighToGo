# ADR-0009: Email as Primary User Identifier

- **Date**: 2026-05-22
- **Status**: Accepted

## Context

The Android predecessor used a username field as the primary account identifier.
The code review of that codebase identified two problems this introduced:

1. `UserDAO` logged the username in plain text at line 329, creating a PII
   exposure path.
2. `SessionManager` reflected distinct error messages for "wrong password" versus
   "username not found", enabling username enumeration by an attacker probing the
   API.

When designing the web rebuild's authentication domain, the team had to choose a
primary identifier for the `User` entity and the login flow.

## Decision

Use email address as the sole primary user identifier. There is no username
field in the web rebuild.

- Registration requires a valid email address.
- Login accepts email + password.
- The `users` table has a unique, case-insensitive index on `email` (CITEXT in
  PostgreSQL).
- No display name is used as a login credential; it is a presentation-layer
  attribute only.

## Rationale

- **Eliminates a class of enumeration risk.** A username-based system makes it
  easy for callers to probe which identifiers are registered by registering their
  own accounts and observing the distinct error paths. Email-as-identifier, combined
  with the generic error policy (ADR-0010), removes this surface: a registration
  attempt on an already-registered email returns the same opaque error as any
  other failure.
- **Industry default for web authentication.** Users expect to log in with the
  account they already manage. A separate username layer adds friction with no
  security or usability benefit at this application's scope.
- **Supports password reset.** A verified email address is a pre-requisite for
  any future "forgot password" flow. Without it, account recovery requires an
  out-of-band channel.
- **Reduces PII surface.** The Android app logged `username` — a value the user
  explicitly chose to be human-readable, and therefore potentially identifiable.
  Email is still PII, but its use is confined to the authentication bounded context
  and masked in all log output (ADR-0011).

## Alternatives Considered

- **Username only** — Retains the Android approach. Rejected because it
  reintroduces the enumeration surface and removes the password-recovery path.
- **Phone number** — An option for some consumer applications. Rejected because
  it adds SMS delivery infrastructure (already deferred from the Android app),
  requires phone number validation, and creates a heavier verification burden for
  the academic scope of this project.
- **OAuth-only (no local credentials)** — Delegates authentication entirely to a
  third-party provider. Rejected because it removes the opportunity to demonstrate
  secure credential storage, hashing, and token management — which are explicit
  learning objectives for this enhancement.
- **Username + email (both required)** — Adds complexity with no benefit. If
  email is present and unique, a separate username is redundant for authentication.

## Consequences

- **Positive**: No username enumeration via registration probing. Password
  recovery flow is unblocked. Simpler `User` entity with one fewer credential
  field.
- **Negative**: Users cannot choose a memorable login handle. If a user changes
  their email address, the identifier changes — this requires a verified-email
  update flow in a future milestone.
- **Follow-ups**: ADR-0010 (generic error policy), ADR-0011 (PII masking
  ensures email is never logged in plain text), future ADR for email change flow.

## References

- SRS §6 FR-A-1 through FR-A-3 (registration requirements).
- Android code review finding: `UserDAO` line 329, username logged in plain text.
- OWASP Authentication Cheat Sheet — username enumeration section.

## Related ADRs

- **ADR-0010** — Generic Authentication Error Policy: the companion decision
  that closes the enumeration surface at the error-response layer.
- **ADR-0011** — PII Masking in Logs: ensures email values in structured log
  fields are masked before emission.

---

**Last Updated**: 2026-05-22
**Author**: Rick Goshen
**Approved By**: Technical Lead
