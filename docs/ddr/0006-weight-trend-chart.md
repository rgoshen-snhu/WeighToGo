# DDR-0006: Weight Trend Chart

- **Date**: 2026-05-29
- **Status**: Accepted

## Context

FR-D-2 requires a line chart of weight over time with selectable date ranges (7 days, 30 days, 90 days, all time). FR-D-3 requires a weekly rate-of-change figure derived from a rolling average. Both surface on the Dashboard alongside the existing latest-entry, total-entries, and goal-progress cards.

The chart is the primary articulation surface for the rate-of-change algorithm, so its design must keep the data legible to every user. Three accessibility constraints govern the design:

- **NFR-A-1** — WCAG 2.1 AA conformance, verified by axe-core via Playwright.
- **NFR-A-3** — screen reader support: every meaningful element exposes an accessible name; non-text content (the chart) needs a text alternative.
- **NFR-A-4** — colour contrast: 4.5:1 for normal text, 3:1 for large text and graphical objects.

A data visualization is non-text content. A line chart alone, however well-rendered, is not perceivable by a screen-reader user. This is the central risk for this work and the reason a charting-library choice cannot be made on visual merit alone.

## Decision

**Charting library: Recharts (v3.x).**

- **Range selector:** MUI `ToggleButtonGroup` with four options labelled "7 days", "30 days", "90 days", "All". The group carries an `aria-label` ("Trend range") and exclusive single-selection. The backend returns the full ("all") series once; the four ranges are computed client-side by filtering the series, avoiding redundant indexed reads.
- **Chart:** Recharts `ResponsiveContainer` wrapping a `LineChart` with a single `Line` (weight over `observation_date`), `XAxis`, `YAxis`, and `Tooltip`. The chart is wrapped in a labelled region (`role="figure"` with an `aria-label` describing the chart) so it has an accessible name independent of Recharts internals.
- **Text/table alternative:** a visually-hidden HTML `<table>` (a `caption`, and `Date` / `Weight` column headers) mirrors the currently-selected series row-for-row. This is the screen-reader and text alternative required by NFR-A-3. It updates with the range selector so the alternative always matches what sighted users see.
- **Empty state:** when the series is empty the component renders an explicit "No trend data yet" message instead of an empty axis frame.
- **Colour & contrast:** the line uses the MUI theme primary colour, which is verified ≥3:1 against the chart background per NFR-A-4 (graphical-object contrast). Axis tick labels and the table text use the theme text colour at ≥4.5:1. The trend is never conveyed by colour alone — the table alternative and axis values carry the data textually (WCAG 1.4.1).

**Rate of change (FR-D-3):** rendered in a sibling `RateOfChangeCard` that mirrors the `GoalProgressCard` prop and state pattern (loading / error / data). It shows the weekly rate with a unit and direction wording, and an explicit "Not enough data yet" state when the backend reports insufficient data.

## Rationale

- **Recharts over alternatives.** Recharts 3.x enables an accessibility layer by default: it sets `role="application"`, adds the chart to the tab order, and provides `ArrowLeft`/`ArrowRight` keyboard navigation across data points with screen-reader announcements (verified against current Recharts documentation). It is a declarative React + SVG component library that fits the existing component-composition style, and it is the library the SRS §15 milestone roadmap names for FR-D-2. Victory and Nivo offer comparable charts but weaker default keyboard/ARIA behaviour and a heavier bundle; a hand-rolled SVG chart would reimplement axis scaling, responsiveness, and accessibility from scratch (YAGNI). Recharts is the lowest-risk path to an accessible chart.
- **`role="application"` is not a text alternative.** Recharts' built-in accessibility helps keyboard users navigate points, but `role="application"` traps assistive-technology virtual-cursor browsing and conveys nothing about the overall trend. A redundant visually-hidden data table is the established technique for making a chart's data perceivable; it is what axe and manual screen-reader review expect. Providing both means keyboard users get point-by-point navigation and screen-reader users get the full series as a table.
- **Client-side range filtering.** The full series is small (one point per day) and is already produced for the dashboard read. Filtering client-side avoids four round-trips and four indexed reads for what is one user's recent history, and keeps the range selector instant.
- **Card pattern reuse for rate-of-change.** Reusing the `GoalProgressCard` loading/error/empty structure keeps the dashboard cards consistent and avoids reinventing state handling (DRY).

## Impact

- `web/frontend/src/features/dashboard/components/WeightTrendChart.tsx` — new component (range selector, Recharts line chart, visually-hidden data table, empty state).
- `web/frontend/src/features/dashboard/components/RateOfChangeCard.tsx` — new card consuming the rate-of-change figure.
- `web/frontend/src/features/dashboard/pages/DashboardPage.tsx` — renders both when entries exist.
- `web/frontend/src/features/dashboard/api/dashboard-client.ts` — response type extended with `trend` and `rate_of_change`.
- `web/frontend/package.json` — adds the `recharts` dependency.
- `web/frontend/e2e/dashboard-trends-a11y.spec.ts` — axe scan over the populated dashboard.

## Visual Reference

```
Weight Trend                          [7d] [30d] [90d] [All]
   lbs
 200 |•
 190 |  •—•
 180 |       •—•—•
 170 |                •
     +------------------------------  date
        (Recharts line chart)

(visually hidden, for screen readers)
   Table: "Weight trend"
   | Date       | Weight   |
   | 2026-05-01 | 200 lbs  |
   | ...        | ...      |

Rate of Change
   Down 0.8 lbs / week        (or: "Not enough data yet")
```

State table:

| State | Chart | Table alternative | Rate card |
|---|---|---|---|
| No entries | "No trend data yet" | Empty/omitted | "Not enough data yet" |
| Sparse / single entry | Renders available points | Mirrors points | "Not enough data yet" |
| Sufficient history | Full line chart | Mirrors series | "Up/Down X / week" |
