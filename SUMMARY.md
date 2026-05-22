# Summary

This file is the durable, reverse-chronological narrative log for the CS 499
capstone work on this repository. The newest entry is at the top. Each entry
records what was done, how it was done, any issues encountered, and how those
issues were resolved.

---

## Phase 2 Follow-up — Documentation Hygiene (2026-05-22)

**What was done**

- Cleared repository-wide documentation debt that the Phase 2
  documentation sweep surfaced and that was deliberately scoped out of
  the restructure pull request (#19) to keep that change focused.
  Tracked as issue #20; with this work merged, Phase 2 is complete.
- Removed every live AI-tool reference from committed documentation: a
  tooling-attribution line in the Android code quality audit, two
  references in the Milestone Two brief, an attribution and a local
  tool-config path in the Phase 7 SMS testing guide, a local
  tool-config path in the Phase 8 manual test scenarios, and an aside
  in the SRS introduction.
- Removed every citation of the root project instruction file from
  other documentation: three reference-table rows and a constraints
  paragraph in the Milestone Two brief, roughly two dozen citations in
  the Android code quality fix plan (violation labels, workflow
  references, and example-commit-message footers), and one in the
  manual testing checklist.
- Repaired corrupted shell commands across three testing documents
  (two manual-testing command guides and the testing-directory
  README). A botched find/replace had merged the Android application
  package token into adjacent words, dropped a path separator, and —
  in one guide — left a misspelled package name and a wrong database
  filename. Restructure-induced build, source, and data paths were
  corrected, and a post-restructure path note was added to each
  repaired guide.
- Corrected retired-tracker references (`TODO.md`,
  `project_summary.md`) in the actively-maintained testing-directory
  README, while leaving such references intact in frozen historical
  material where they accurately record the project's state at the
  time of writing.
- Replaced a `v2.x` milestone-release version scheme with honest
  `0.x` development versioning across the SRS and the Milestone Two
  brief, since the web application is in initial, pre-1.0 development.
- Delivered as PR #21, branch `docs/m2-phase-2-doc-hygiene`.

**How it was done**

- Branched `docs/m2-phase-2-doc-hygiene` from the latest `main` after
  the Phase 2 restructure pull request merged.
- A read-and-verify documentation sweep opened every in-scope document
  in full; repository-wide searches then confirmed that issue #20's
  diagnosis of AI-tool and instruction-file references was complete.
- The repository owner chose, per file, to repair the corrupted
  command guides in place rather than archive or delete them. Ground
  truth for the repair — application package, Gradle module name,
  launcher activity, and database filename — was read directly from
  the Android sources.
- The corrupted commands were repaired with a scripted, systematic
  pass and then verified line by line.
- The retired-tracker policy was applied by classification: frozen
  historical documents keep their references as accurate history;
  actively-maintained documents have them corrected.
- Work was committed as a sequence of small, atomic commits, one per
  debt category.
- Three review passes — code, adversarial, and security — were run on
  the branch; their findings are recorded below.

**Issues encountered**

- The read-and-verify sweep found one AI-tooling reference in the SRS
  introduction that issue #20's original diagnosis had not listed.
- The corruption in the testing commands was more systematic than
  stale paths: a find/replace had merged shell tokens, dropped a path
  separator, misspelled the package name, and used the wrong database
  filename.
- The adversarial review found a third corrupted snippet — in the
  testing-directory README — and one restructure-stale path that the
  first repair pass had missed.
- The adversarial review also flagged the same wrong package and
  database names in a test-helper script outside this issue's
  documentation scope.

**How issues were resolved**

- The additional SRS reference was surfaced to the repository owner,
  who chose to remove it; it was removed alongside the other AI-tool
  references.
- The corrupted commands were repaired against ground truth from the
  Android sources and verified to contain no residual corruption.
- The third corrupted snippet and the stale path from the adversarial
  review were repaired the same way in follow-up commits and
  re-verified.
- The out-of-scope script defect was surfaced to the repository owner
  as a separate decision rather than folded into this issue.

---

## Phase 2 — Repository Restructure (2026-05-21)

**What was done**

- Restructured the repository from an Android-only layout into a polyglot
  monorepo: the entire Android Gradle project moved from the repository root
  into `android/`, and `web/frontend/` and `web/backend/` were created as
  tracked placeholders for the web rebuild.
- Tagged `v1.0.0-android` on the final pre-restructure commit of `main`,
  marking the end of the Android-only era. The restructure commit itself is not
  separately tagged — it is a structural change, not a release.
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
- Delivered as PR #19, branch `feature/m2-phase-2-repo-restructure`.

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
- Three review passes — code, adversarial, and security — were run on PR #19;
  their findings are recorded below.

**Issues encountered**

- `local.properties` was listed for relocation but is machine-specific and
  git-ignored, so it could not be moved with `git mv`.
- The Android CI workflow's report and artifact paths referred to a module
  named `app`, but the actual module is `weightogo` — a stale reference that
  predated this phase.
- The SRS carried two ADR cross-references that pointed at the wrong ADR
  independently of the renumbering.
- A thorough documentation sweep surfaced pre-existing documentation debt wider
  than this phase's scope: corrupted command snippets in `docs/testing/`, live
  AI-tool references and project-instruction-file citations in several committed
  documents, and retired tracker references.
- The review passes flagged three documentation and configuration gaps: the
  expanded `.gitignore` did not ignore `.env` files; the README
  repository-layout tree omitted several directories; and the SRS ADR-index
  subsection was still headed "Planned" although two of its ADRs are now
  written.

**How issues were resolved**

- `local.properties` was excluded from the tracked move and copied into
  `android/` instead, where the existing ignore rule still covers it; the
  Android build locates the SDK correctly at the new path.
- The CI paths were corrected to `android/weightogo/build/...` in the same
  change that repointed the workflow at the new directory, fixing the stale
  module name and the new path layer together.
- The two mis-targeted SRS references were corrected to their proper ADRs while
  the index was renumbered, leaving the SRS internally consistent.
- That debt predates this phase. It is tracked as Phase 2 follow-on work in
  issue #20 — a dedicated documentation-hygiene pass delivered as its own pull
  request — rather than expanding the restructure PR.
- The three review findings were resolved on the PR: an `.env` ignore rule was
  added (with `.env.example` kept tracked), the README layout tree was
  completed, and the SRS subsection heading was corrected. The security pass
  found no vulnerabilities.

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
