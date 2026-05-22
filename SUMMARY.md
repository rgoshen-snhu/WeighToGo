# Summary

This file is the durable, reverse-chronological narrative log for the CS 499
capstone work on this repository. The newest entry is at the top. Each entry
records what was done, how it was done, any issues encountered, and how those
issues were resolved.

---

## Phase 2 — Repository Restructure (2026-05-21)

**What was done**

- Restructured the repository from an Android-only layout into a polyglot
  monorepo: the entire Android Gradle project moved from the repository root
  into `android/`, and `web/frontend/` and `web/backend/` were created as
  tracked placeholders for the web rebuild.
- Marked the project's two eras with annotated tags: `v1.0.0-android` on the
  final pre-restructure commit of `main`, and `v1.1.0-web` — applied after this
  phase merges — on the restructured `main`.
- Updated the Android CI workflow to build from `android/`, corrected its
  report and artifact paths, and path-filtered its triggers so it runs only for
  Android changes.
- Extended `.gitignore` with Python and Node sections ahead of the web stack.
- Added ADR-0007 (rebuild as a full-stack web application) and ADR-0008
  (polyglot monorepo); renumbered the SRS ADR index and every in-text ADR
  reference to the seven-ADR M2 set.
- Rewrote the root `README.md` around the monorepo layout and the mobile-to-web
  narrative, resolving the two pre-existing `README.md` defects flagged in
  Phase 1 — the broken `TODO.md` links and the stale project-structure tree.
- Pointed the CONTRIBUTING Android setup instructions at the new `android/`
  path.
- Delivered on branch `feature/m2-phase-2-repo-restructure`.

**How it was done**

- Branched `feature/m2-phase-2-repo-restructure` from the latest `main`.
- Every Android file was relocated with `git mv` so the move is recorded as a
  set of pure renames; `git log --follow` confirmed that history, blame, and
  log all trace through the move.
- The relocated Android build was verified before any further change:
  `./gradlew test`, `lint`, and `assembleDebug` all pass at the new path with
  no source modifications.
- The work was committed as a sequence of small, atomic commits — the move, the
  CI change, the web scaffold, the ignore rules, the ADRs, the SRS renumber,
  and the documentation updates each as their own commit.
- A documentation sweep was run as the pre-push gate, updating the README,
  CONTRIBUTING, the SRS, and this log.

**Issues encountered**

- `local.properties` was listed for relocation but is machine-specific and
  git-ignored, so it could not be moved with `git mv`.
- The Android CI workflow's report and artifact paths referred to a module
  named `app`, but the actual module is `weightogo` — a stale reference that
  predated this phase.
- The SRS carried two ADR cross-references that pointed at the wrong ADR
  independently of the renumbering.
- Several historical testing documents under `docs/testing/` contain stale
  Gradle paths.

**How issues were resolved**

- `local.properties` was excluded from the tracked move and copied into
  `android/` instead, where the existing ignore rule still covers it; the
  Android build locates the SDK correctly at the new path.
- The CI paths were corrected to `android/weightogo/build/...` in the same
  change that repointed the workflow at the new directory, fixing the stale
  module name and the new path layer together.
- The two mis-targeted SRS references were corrected to their proper ADRs while
  the index was renumbered, leaving the SRS internally consistent.
- The `docs/testing/` staleness predates this phase and is unrelated to the
  restructure; it was left for a later consolidated documentation pass and
  noted on the pull request rather than expanding this phase's scope.

---

## Phase 1 — Tracking Log Scaffold (2026-05-21)

**What was done**

- Added this `SUMMARY.md` file at the repository root: the durable,
  reverse-chronological narrative log for the milestone, with the newest entry
  prepended at the top.
- Seeded the log with two entries — this Phase 1 entry and the Phase 0 entry
  below it — so the record is complete from the start of the milestone.
- Delivered as PR #18, branch `docs/m2-phase-1-summary-scaffold`.

**How it was done**

- Branched `docs/m2-phase-1-summary-scaffold` from the latest `main`.
- The Phase 0 entry was carried forward from the breakdown prepared at the close
  of Phase 0 and recorded on the Phase 1 tracking issue (#7), then verified
  against the merged Phase 0 pull request before inclusion; no changes were
  needed.
- The file was checked through the GitHub Markdown renderer to confirm both
  entries display correctly.
- A documentation sweep was run as the pre-push gate. It confirmed `SUMMARY.md`
  is the only document this phase needs to add or change. The sweep also noted
  pre-existing staleness in the root `README.md` — a project-structure tree
  predating the repository restructure, and two links to the retired `TODO.md`
  task tracker — which is out of scope for this phase and is left for the README
  revisions scheduled in the repository-restructure phase (Phase 2) and the
  documentation-closeout phase (Phase 9).
- Three review passes — code, adversarial, and security — were run on PR #18.

**Issues encountered**

- None arose in this phase's own work: adding a single documentation file raised
  no blocker or defect, and there is no application code, test, or build impact.
  The documentation sweep's observation about pre-existing `README.md` staleness,
  noted above under "How it was done", is a deferred out-of-scope item rather
  than an issue in this phase.

**How issues were resolved**

- Not applicable.

---

## Phase 0 — Repository & Project Setup (2026-05-21)

**What was done**

- Renamed the working repository on GitHub: `rgoshen-snhu/cs360-WeightToGoMobile`
  → `rgoshen-snhu/WeighToGo`; updated the local `snhu` remote and the `gh`
  default repo.
- Stood up GitHub project tracking: a Project board ("WeighToGo — CS 499
  Capstone"), four epic issues (M2 #2, M3 #3, M4 #4, Final #5), and ten M2 phase
  issues (Phases 0–9, issues #6–#15) attached as sub-issues of the M2 epic.
- Updated old repository-name references in the SRS, README, and CONTRIBUTING;
  fixed a broken CI badge and placeholder repository URLs.
- Added a `## Tasks` section to the issue templates; relocated the Android
  development journal to `docs/history/android_summary.md` and documented the
  new directory with a README.
- Removed two unused legacy GitHub Actions workflows left from an earlier
  integration setup.
- Delivered as PR #16, branch `chore/m2-phase-0-repo-project-setup`.

**How it was done**

- Repository renamed with `gh repo rename`; GitHub's automatic old-URL redirect
  verified (HTTP 301).
- Board, epics, and phase issues created with the `gh` CLI; phase issues linked
  as sub-issues via the GitHub sub-issue API; all issues added to the board.
- Documentation edits were surgical — only repository-name references were
  changed; historical mentions in the SRS naming-considerations narrative were
  deliberately preserved.
- The core change was committed as two atomic commits (`chore:` templates +
  journal relocation, `docs:` repo-name updates), with follow-up commits for
  review findings and owner-directed changes.
- Three review passes — code, adversarial, and security — were run on PR #16.

**Issues encountered**

- The `gh` token lacked the `project` OAuth scope, blocking Project board
  creation.
- The journal relocation broke a relative link in `docs/testing/README.md`
  (review finding W1).
- Two unused legacy GitHub Actions workflows were present; the automated review
  workflow failed on every pull request for lack of a configured token secret.
- The newly created `docs/history/` directory was initially undocumented
  (adversarial review note N1).
- Phase 0 expanded beyond the original plan during execution, at the repository
  owner's direction.

**How issues were resolved**

- The owner refreshed the `gh` token with the `project` scope.
- W1 was fixed during the phase — the link was repointed to
  `../history/android_summary.md`.
- The two legacy workflows were removed (owner-directed) after verifying they
  had no branch-protection or file dependencies.
- A README was added for `docs/history/`, resolving N1.
- Broader `docs/` indexing was captured as a separate tracked issue (#17) under
  the M2 epic rather than expanding Phase 0 further.
