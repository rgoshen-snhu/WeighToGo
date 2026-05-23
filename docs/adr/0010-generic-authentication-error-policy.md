# ADR-0010: Generic Authentication Error Policy

- **Date**: 2026-05-22
- **Status**: Accepted

## Context

The Android predecessor's `SessionManager` returned distinct error messages
depending on the failure mode: a different message was returned when a username
was not found versus when the password was wrong. The code review identified this
as a username enumeration vulnerability — an attacker could probe the login
endpoint to determine which email addresses have registered accounts simply by
observing the difference in responses.

When designing the web rebuild's authentication endpoints, the team had to
decide how to communicate authentication failures to callers.

## Decision

Every authentication failure — wrong password, unknown email, locked account
state visible to the caller, missing token, expired token — returns the same
generic HTTP response body:

```json
{"detail": "Invalid credentials."}
```

The HTTP status codes distinguish broad categories (401 Unauthorized for
credential failures, 423 Locked for explicit lockout notification, 409 Conflict
for duplicate registration) but the response body never confirms whether a
specific email address exists in the system.

This policy applies to:
- `POST /auth/login` — wrong password and unknown email both return 401 with
  the same body.
- `POST /auth/register` — duplicate email returns 409 with a generic body that
  does not say "email already registered".
- `POST /auth/refresh` — invalid or replayed refresh tokens return 401 with the
  same body.
- `GET /auth/me` — missing or expired access token returns 401.

## Rationale

- **Closes the enumeration finding directly.** If every failure path returns
  identical output, an attacker probing `POST /auth/login` with a known-bad
  password learns nothing about whether the email is registered. The response is
  indistinguishable from a probe against a non-existent address.
- **OWASP alignment.** The OWASP Authentication Cheat Sheet explicitly recommends
  generic error messages for authentication failures to prevent user enumeration.
- **Minimal implementation cost.** A single shared error constant and a
  consistent `raise HTTPException(401, detail=_GENERIC_AUTH_ERROR)` pattern is
  simpler to maintain than distinct messages that must be kept consistent.

## Alternatives Considered

- **Specific error codes per failure type** — e.g., distinguish "email not
  found" from "wrong password". Rejected. This directly enables enumeration and
  reproduces the Android finding.
- **Distinct HTTP status codes per failure type without body variation** — e.g.,
  404 for unknown email, 401 for wrong password. Rejected. HTTP status codes are
  still observable; using 404 for "email not found" leaks the same information
  as a distinct message body.
- **Generic errors for external callers, specific errors in logs** — Already the
  case: structured log events (`login_failed`, `account_locked`) carry internal
  context for debugging without that context reaching the API response.

## Consequences

- **Positive**: Username enumeration via login probing is closed. The
  error-handling code is simpler — one constant, one status code for the common
  credential-failure path.
- **Negative**: Legitimate users who mis-type their email address receive no
  feedback distinguishing "email not found" from "wrong password". This is a
  deliberate UX trade-off in favour of security. The password-reset flow
  (deferred to a later milestone) is the intended recovery path.
- **Follow-ups**: The account lockout notification (423 Locked) is an
  intentional exception to full opaqueness — it tells the user their account is
  locked without confirming credential correctness. This is acceptable because
  the lockout state is triggered by prior confirmed access attempts, not by
  probing.

## References

- SRS §6 FR-A-6 (generic error messages requirement).
- SRS §7 NFR-S-7 (username enumeration prevention).
- Android code review finding: `SessionManager` distinguishable error paths.
- OWASP Authentication Cheat Sheet.

## Related ADRs

- **ADR-0009** — Email as Primary Identifier: the companion decision that
  removes the username field entirely, reducing the enumerable surface to one
  identifier type.
- **ADR-0011** — PII Masking in Logs: ensures that even internal log events
  recording auth failures do not emit plain-text email addresses.

---

**Last Updated**: 2026-05-22
**Author**: Rick Goshen
**Approved By**: Technical Lead
