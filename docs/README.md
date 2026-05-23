# Documentation

This directory holds all documentation for the WeighToGo repository — both the
preserved Android artifact and the CS 499 web rebuild. Use this page as the
entry point for anything under `docs/`.

## Authority

When two documents disagree, use this order of precedence:

1. **`specs/WeighToGo_Web_SRS_v2.md`** — authoritative system spec for the web
   rebuild. Wins over every other web-related doc.
2. **`plans/milestone-two-plan.md`** — the active CS 499 Milestone Two
   implementation brief. References sections of the SRS that are in scope for
   M2.
3. **`adr/` and `ddr/`** — point-in-time decisions; superseded entries are
   marked in their own status field, not deleted.
4. **`architecture/`** — Android-era technical docs. Historical reference only
   for the web rebuild.

## Quick links

- **System spec (web):** [`specs/WeighToGo_Web_SRS_v2.md`](specs/WeighToGo_Web_SRS_v2.md)
- **Active milestone plan:** [`plans/milestone-two-plan.md`](plans/milestone-two-plan.md)
- **Code review checklist:** [`standards/cs499_code_review_checklist.md`](standards/cs499_code_review_checklist.md)
- **ADR index:** [`adr/README.md`](adr/README.md)
- **DDR index:** [`ddr/README.md`](ddr/README.md)

## Subdirectories

| Path | Purpose |
|---|---|
| [`adr/`](adr/) | Architecture Decision Records (cross-stack). See [ADR index](adr/README.md). |
| [`api/`](api/) | API artifacts. Holds the OpenAPI snapshot (`openapi.json`) for the web backend. |
| [`architecture/`](architecture/) | Android-era architecture docs. Historical; superseded by the SRS for the web rebuild. |
| [`ddr/`](ddr/) | Design Decision Records (UI/UX choices). See [DDR index](ddr/README.md). |
| [`design/`](design/) | Figma specs and design references for the Android UI. |
| [`history/`](history/) | Pre-restructure Android artifacts and summary of the original codebase. |
| [`plans/`](plans/) | Milestone implementation briefs and historical planning docs. |
| [`requirements/`](requirements/) | Original CS 360 course assignment requirements (historical). |
| [`screenshots/`](screenshots/) | Verification screenshots produced during phase work. |
| [`specs/`](specs/) | Authoritative system specifications (currently: the web SRS). |
| [`standards/`](standards/) | Code review checklists and quality standards applied across the repo. |
| [`testing/`](testing/) | Manual test plans, scenario guides, and Android-era testing docs. |
| [`user-guide/`](user-guide/) | End-user documentation (placeholder; populated in a later milestone). |
