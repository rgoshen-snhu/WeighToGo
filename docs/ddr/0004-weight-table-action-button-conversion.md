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

The decision has two complementary parts: a structural rewrite of the row controls (Button-with-label instead of icon-only IconButton) and a theme-level floor that closes NFR-A-5 across the entire app.

### Structural change (WeightEntryTable.tsx)

Replace each row's `IconButton size="small"` (Edit and Delete) with an MUI `Button` rendered with:

- `variant="outlined"`
- `startIcon={<EditIcon />}` / `startIcon={<DeleteIcon />}`
- `sx={{ mr: 1 }}` on the leading Edit button for inter-action spacing
- The original `aria-label` strings (`Edit entry from {date}` / `Delete entry from {date}`) preserved verbatim so existing E2E selectors keep working
- Delete keeps `color="error"` to preserve the destructive-action visual cue

The redundant `Tooltip` wrappers and the inline `<span style={{ marginLeft: 4 }}>` label hack are dropped — the Button's native text label already carries the action name. `size="medium"` is omitted because it is the MUI default; specifying it implies a deliberate non-default choice and adds copy-paste noise on any future button.

### Target-size floor (theme.ts)

Add `components.MuiButton.styleOverrides.root = { minHeight: 44, minWidth: 44 }` and the same on `MuiIconButton`. The override targets these two components only — **not** `MuiButtonBase`. `MuiButtonBase` is also the root for `Checkbox`, `Radio`, `Tab`, `MenuItem`, `ToggleButton`, and `ListItemButton`; a blanket 44px floor on the base class would visually regress those denser controls (a 44px MenuItem cascades into uncomfortably tall menus, a 44px Tab strip wastes vertical space, etc.).

Targeting `MuiButton` + `MuiIconButton` covers every interactive control in the current app that risks falling below the floor, and any future button instance — including third-party feature additions — inherits the floor by default rather than requiring per-call-site discipline.

## Rationale

- **Accessibility — SRS NFR-A-5.** A 44 × 44 CSS pixel minimum is a hard requirement in the SRS and a published WCAG 2.2 success criterion (2.5.8 Target Size — Minimum). Enforcing it in the theme makes compliance the default and removes a class of forget-it-on-the-next-button regressions: a new button anywhere in the app inherits the floor without the author needing to know NFR-A-5 exists.
- **Right altitude for the fix.** A per-component `sx={{ minHeight: 44 }}` adds compliance one button at a time and leaves sibling controls (e.g., the avatar `IconButton` in `UserMenu.tsx` and the mobile-nav hamburger `IconButton` in `AppLayout.tsx`) silently violating the same NFR. The theme override closes all three at once because each control already extends the affected MUI component classes.
- **Idiomatic MUI for the row controls.** `Button` with `startIcon` is the documented MUI pattern for a labeled icon control. The previous design pushed an `IconButton` past its intended role by stuffing a `<span>` label inside it, which is why a `Tooltip` was needed in the first place to repeat the same text on hover. Switching to `Button` collapses three indirections (icon, hand-positioned label span, tooltip) into one component with the label permanently visible.
- **Discoverability and parity with the row context.** A visible "Edit" / "Delete" label is unambiguous in a tabular list where many actions could plausibly attach to the same icon. The outlined variant keeps the controls visually distinct from row data and from the page's primary "Add entry" CTA, which uses `variant="contained"`.
- **Testability.** The component test wraps the render in `ThemeProvider` so the theme override actually applies, then asserts `toHaveStyle({ minHeight: '44px', minWidth: '44px' })` against both controls. MUI's `styleOverrides` compile to an emotion-generated CSS class injected into the document `<head>`, not an inline `style` attribute, so the matcher resolves the value through `window.getComputedStyle`. The Playwright spec independently asserts the real rendered `boundingBox()` dimensions.

## Alternatives Considered

1. **Per-button `sx={{ minHeight: 44 }}` (the F5 PR's first proposal).** Surgical and visibly tied to the failing finding, but applies the fix at the wrong altitude: NFR-A-5 is an app-wide invariant, not a per-component property. As shipped, two sibling `IconButton` controls (`UserMenu.tsx`, `AppLayout.tsx`) remained ~40 px tall and still violated the NFR after the PR; the next regression has to be hunted button by button. Rejected in favor of the theme override after PR #40 review.
2. **Blanket `MuiButtonBase` override.** Covers every button-derived control with one rule, but cascades the 44px floor into `MenuItem`, `Tab`, `Checkbox`, `Radio`, `ListItemButton`, `ToggleButton`, and similar controls that have their own designed sizing. Rejected because the visual regressions to dense controls outweigh the convenience of one fewer override entry.
3. **Keep `IconButton` but use a larger size preset (`size="large"` or default).** Default `IconButton` renders around 40 px — still under 44. `size="large"` reaches the floor but keeps the controls icon-only, which the existing code already considered insufficient (hence the `<span>` label hack and the `Tooltip`). Rejected because it does not address the discoverability problem.
4. **Keep `IconButton` with `sx={{ minWidth: 44, minHeight: 44 }}`.** Meets the dimension floor but leaves the controls icon-only and still applies at the per-button altitude. Rejected on both axes.
5. **Standalone text label rendered next to the icon (`IconButton` + adjacent `Typography`).** Fragments the click target across two elements, defeats the 44 px guarantee for the label portion, and is not a documented MUI pattern. Rejected.
6. **`ButtonGroup` wrapping both actions.** Visually tighter, but couples two independent semantic actions (a navigation link and a state-mutating button) into a grouped control, which screen readers narrate as a single composite widget. The accessibility tradeoff is wrong for actions whose semantics differ.

## Impact

### Components Modified
- `web/frontend/src/theme/theme.ts` — added `components.MuiButton.styleOverrides.root = { minHeight: 44, minWidth: 44 }` and same on `MuiIconButton`. App-wide effect.
- `web/frontend/src/features/weight/components/WeightEntryTable.tsx` — Edit and Delete cells converted to `Button` with `startIcon` + `variant="outlined"`; `IconButton`, `Tooltip`, and the inline span dropped. No per-button `sx` for the floor — the theme handles it.
- `web/frontend/src/features/weight/components/WeightEntryTable.test.tsx` — extended with two assertions covering both controls (`toHaveStyle({ minHeight: '44px', minWidth: '44px' })`), wrapped in `ThemeProvider` so the theme override applies.
- `web/frontend/e2e/weight-target-size.spec.ts` — Playwright spec asserts real `boundingBox()` width and height are both ≥ 44 px.

### Side Effects (deliberate)
- The avatar `IconButton` in `web/frontend/src/components/UserMenu.tsx` and the mobile-nav hamburger `IconButton` in `web/frontend/src/components/AppLayout.tsx` are now ≥ 44 px without explicit changes to those files. This is the intended behavior of the theme override.

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

Sibling controls (avatar menu in `UserMenu`, hamburger in `AppLayout`) gain the 44 px floor too — same theme override — but are otherwise visually unchanged because they were close to but not above 44 px before.

## References

- **Issue:** GH-34
- **SRS NFR-A-5:** `docs/specs/WeighToGo_Web_SRS_v2.md` — "All interactive targets are at least 44 by 44 CSS pixels."
- **Remediation plan §5:** `docs/standards/M2_WEB_APP_QUALITY.md` — "Weight table action controls likely miss the 44px target requirement."
- **MUI Button (`startIcon`):** https://mui.com/material-ui/react-button/#buttons-with-icons-and-label
- **WCAG 2.2 SC 2.5.8 Target Size (Minimum):** https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
