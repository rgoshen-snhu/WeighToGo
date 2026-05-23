# ADR-0011: PII Masking Strategy in Logs

- **Date**: 2026-05-22
- **Status**: Accepted

## Context

The Android code review identified three locations where personally identifiable
information was written to logs in plain text:

- `SessionManager` lines 139, 190, and 229 logged usernames without masking.
- `UserDAO` line 329 logged phone numbers without masking.

These findings mean a log file or a log aggregation service could expose user
identity and contact information to anyone with log access — a violation of the
principle of minimal PII exposure and a practical compliance risk.

The web rebuild needed a logging strategy that prevented this class of finding
from recurring regardless of which future developer wrote the log statement.

## Decision

PII masking is applied automatically by a structlog processor (`_redact_processor`)
that runs unconditionally on every log event before it is serialised. No caller
is required to sanitise values before passing them to the logger.

The masking rules are:

- **Email addresses** are partially masked: the local part is replaced with
  `***` followed by the last four characters of the local part, and the domain
  is preserved. Example: `rick@example.com` → `***ick@example.com`. This
  preserves enough context for debugging correlation while hiding the full
  address.
- **Phone numbers** matching North American and international formats are
  replaced with the literal `[phone]`.

`mask_pii()` is also available as a public utility for callers that need to
sanitise values before storing them outside of logs (e.g., in error messages
returned to clients).

The processor is registered once in `configure_logging()`, which is called at
application startup. All subsequent log calls — regardless of which logger, which
module, or which bounded context — pass through the redaction step.

## Rationale

- **Defence in depth.** A caller-side masking requirement is fragile: any new
  code path that logs an email or phone without explicitly calling `mask_pii()`
  creates a regression. A central processor eliminates the per-call obligation
  entirely. A future auth path that binds a raw email to a log entry is still
  protected.
- **Closes the Android findings directly.** The three `SessionManager` and one
  `UserDAO` violations were all caller-side omissions. The processor-based
  approach would have prevented all four.
- **Partial masking preserves debuggability.** Replacing the entire email with
  `[email]` makes log correlation impossible — you cannot tell whether two
  events involve the same user. Showing the last four characters of the local
  part and the full domain preserves enough entropy for correlation while hiding
  the identifying prefix.
- **structlog processor chain is the right integration point.** structlog's
  processor chain is designed exactly for cross-cutting transformations on every
  log event. Hooking redaction here is idiomatic and carries no runtime overhead
  beyond the regex substitution itself.

## Alternatives Considered

- **Caller-side masking only** — Each logging call is responsible for calling
  `mask_pii()`. Rejected because it relies on every developer remembering,
  fails silently when forgotten, and directly reproduces the Android findings.
- **Structured log fields with a separate redaction layer** — Log PII in named
  fields (e.g., `email=user@example.com`) and redact those specific field names
  at the aggregator. Rejected because it requires the aggregator to be correctly
  configured, creates a gap between local development and production, and
  still requires callers to avoid embedding PII in the `event` message.
- **Prohibit logging PII fields entirely** — Never log any value that could
  contain PII. Rejected because some PII-adjacent values (a partial email, a
  user ID) are genuinely useful for debugging and incident investigation.
  Total prohibition makes the logs less actionable.
- **Replace every email with `[email]`** — Simpler regex, no partial reveal.
  Rejected because it makes log correlation across events involving the same user
  impossible.

## Consequences

- **Positive**: PII cannot leak through any log call, regardless of caller
  discipline. The Android finding is closed structurally. Partial email
  preservation keeps logs debuggable.
- **Negative**: The processor runs on every log event, adding a small regex
  overhead. The partial email format (`***ick@example.com`) reveals the last four
  characters — not zero PII, but a deliberate trade-off for debuggability.
  Phone masking is total (`[phone]`), which is safe because phone numbers are
  not useful for log correlation.
- **Follow-ups**: If nested data structures (dicts, lists) are ever bound as
  log fields, the processor's current top-level-only iteration will miss nested
  PII. This is an accepted limitation at the current scope where no nested PII
  is passed to loggers; a recursive traversal can be added when needed.

## References

- SRS §6 FR-A-10 (PII-aware logging requirement).
- SRS §7 NFR-Priv-1 (masking format specification).
- Android code review findings: `SessionManager` lines 139, 190, 229;
  `UserDAO` line 329.
- Implementation: `web/backend/src/weighttogo/shared/logging.py`.

## Related ADRs

- **ADR-0009** — Email as Primary Identifier: email is the value most likely to
  appear in auth-related log events.
- **ADR-0010** — Generic Authentication Error Policy: the two decisions together
  ensure that neither log output nor API responses reveal authentication state.

---

**Last Updated**: 2026-05-22
**Author**: Rick Goshen
**Approved By**: Technical Lead
