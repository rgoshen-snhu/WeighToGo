# DDR-0004: Weight Table Action Button Conversion

- **Date**: 2026-05-28
- **Status**: Accepted

## Context

The weight-entry history table at `/weight` exposes Edit and Delete actions on every row. Until F5, both controls were rendered as `IconButton size="small"` with a tiny inline `<span>` label, wrapped in an MUI `Tooltip`:

```tsx
<IconButton size="small" ...>
  <EditIcon fontSize="small" />
  <span style={{ marginLeft: 4 }}>Edit</span>
</IconButton>
```

The M2 Web App Quality Review (`docs/standards/M2_WEB_APP_QUALITY.md` §5) flagged the row actions as a likely violation of **SRS NFR-A-5** ("All interactive targets are at least 44 by 44 CSS pixels"). MUI's small icon-button preset renders at roughly 30 by 30 CSS pixels, which falls below the 44 px floor and risks recreating the Android-era hit-target findings the web rebuild was meant to close. The existing `weight-a11y.spec.ts` axe scan checks for *critical* WCAG violations only — it does not enforce target-size at runtime, so the regression had no automated detector.

This DDR records the visual change that ships with F5 and the rationale for choosing one accessible pattern over the obvious alternatives.

## Decision

Replace each row's `IconButton size="small"` (Edit and Delete) with an MUI `Button` rendered with:

- `size="medium"`
- `variant="outlined"`
- `startIcon={<EditIcon />}` / `startIcon={<DeleteIcon />}`
- `sx={{ minHeight: 44 }}` (and `mr: 1` on the leading Edit button for inter-action spacing)
- The original `aria-label` strings (`Edit entry from {date}` / `Delete entry from {date}`) preserved verbatim so existing E2E selectors keep working
- Delete keeps `color="error"` to preserve the destructive-action visual cue

The redundant `Tooltip` wrappers and the inline `<span style={{ marginLeft: 4 }}>` label hack are dropped — the Button's native text label already carries the action name.

## Rationale

- **Accessibility — SRS NFR-A-5.** A 44 by 44 CSS pixel minimum is a hard requirement in the SRS and a published WCAG 2.2 success criterion (2.5.8 Target Size — Minimum). Setting `minHeight: 44` on the Button via `sx` enforces the floor declaratively without overriding MUI's theme tokens, and the medium-sized text Button reaches the minimum width naturally through its label + start-icon padding.
- **Idiomatic MUI.** `Button` with `startIcon` is the documented MUI pattern for a labeled icon control. The previous design pushed an `IconButton` past its intended role by stuffing a `<span>` label inside it, which is why a `Tooltip` was needed in the first place to repeat the same text on hover. Switching to `Button` collapses three indirections (icon, hand-positioned label span, tooltip) into one component with the label permanently visible.
- **Discoverability and parity with the row context.** A visible "Edit" / "Delete" label is unambiguous in a tabular list where many actions could plausibly attach to the same icon. The outlined variant keeps the controls visually distinct from row data and from the page's primary "Add entry" CTA, which uses `variant="contained"`.
- **Testability.** The change makes the controls assertable two different ways: a JSDOM component test can read `minHeight: 44px` from the inline style block (MUI's `sx` emits this directly), and a Playwright spec can read the rendered `boundingBox()` and assert real pixel dimensions. F5 ships both gates.

## Alternatives Considered

1. **Keep `IconButton` but use a larger size preset (`size="large"` or default).** Default `IconButton` renders around 40 px — still under 44. `size="large"` reaches the floor but keeps the controls icon-only, which the existing code already considered insufficient (hence the `<span>` label hack and the `Tooltip`). Rejected because it does not address the discoverability problem and still requires a manual `sx` override to guarantee 44 px in every theme density.
2. **Keep `IconButton` with `sx={{ minWidth: 44, minHeight: 44 }}` (the M2 quality review's first-listed suggestion).** Meets the dimension floor but leaves the controls icon-only. The review itself ranks this lowest of three suggestions ("Prefer icon-only buttons with accessible labels, **or use normal Button controls if text must remain visible**"). The existing layout already wanted a visible label — that is why the `<span>` hack was there — so the icon-only path loses information the previous design was trying to convey.
3. **Standalone text label rendered next to the icon (`IconButton` + adjacent `Typography`).** Fragments the click target across two elements, defeats the 44 px guarantee for the label portion, and is not a documented MUI pattern. Rejected.
4. **`ButtonGroup` wrapping both actions.** Visually tighter, but couples two independent semantic actions (a navigation link and a state-mutating button) into a grouped control, which screen readers narrate as a single composite widget. The accessibility tradeoff is wrong for actions whose semantics differ.

## Impact

### Components Modified
- `web/frontend/src/features/weight/components/WeightEntryTable.tsx` — Edit and Delete cells converted; `IconButton` and `Tooltip` imports removed; `Button` import added.
- `web/frontend/src/features/weight/components/WeightEntryTable.test.tsx` — extended with two assertions (`toHaveStyle({ minHeight: '44px' })`) covering both controls.
- `web/frontend/e2e/weight-target-size.spec.ts` — new Playwright spec asserting `boundingBox()` width and height are both ≥ 44 px after a real render.

### Visual Change
- **Before:** two small (~30 px) icon buttons with the action word jammed inside as a non-standard inline span, tooltip on hover.
- **After:** two outlined medium Buttons with a leading icon and a permanently visible label, side-by-side, each at least 44 px tall.

### Screens Affected
- `/weight` (the only page that renders `WeightEntryTable`).
- Dashboard summary card is unaffected; it does not embed this table.

### Behavioral Compatibility
- `aria-label` strings are unchanged, so the existing `weight-edit.spec.ts` and `weight-delete.spec.ts` selectors continue to resolve. Existing component tests (`renders Edit links`, `renders the correct number of rows`, `calls onDelete when Delete button is clicked`) all still pass without modification because they query by role and accessible name, not by element tag.

## Visual Reference

The change is visible on `/weight` once the user has at least one entry. Before/after capture is best taken with the standard E2E user (`weight-create.spec.ts` seed). Verbal description for reviewers without local screenshots:

```
Before:  [✎] Edit   [🗑] Delete       ← ~30 px, icon-prominent, label as inline span
After:   [✎ Edit]  [🗑 Delete]        ← 44 px+, outlined buttons, label is the affordance
```

## References

- **Issue:** GH-34
- **SRS NFR-A-5:** `docs/specs/WeighToGo_Web_SRS_v2.md` — "All interactive targets are at least 44 by 44 CSS pixels."
- **Remediation plan §5:** `docs/standards/M2_WEB_APP_QUALITY.md` — "Weight table action controls likely miss the 44px target requirement."
- **MUI Button (`startIcon`):** https://mui.com/material-ui/react-button/#buttons-with-icons-and-label
- **WCAG 2.2 SC 2.5.8 Target Size (Minimum):** https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
