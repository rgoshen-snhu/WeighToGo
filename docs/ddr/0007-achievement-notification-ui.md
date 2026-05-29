# DDR-0007: Achievement Notification UI

- **Date**: 2026-05-29
- **Status**: Accepted

## Context

FR-N-1 requires a celebratory in-app notification when an achievement is earned
during a weight entry session.  Notifications must be accessible (ARIA live
region, NFR-A-3) and must respect `prefers-reduced-motion` (NFR-A-6).

## Decision

**MUI Snackbar + Alert toast, bottom-center, auto-hides after 6 seconds.**

- `role="status"` on the Alert provides a polite ARIA live region so screen
  readers announce the achievement without interrupting the user's current
  context.
- The MUI `Slide` transition is replaced with `Fade` when
  `window.matchMedia('(prefers-reduced-motion: reduce)').matches` is true.
- Multiple achievements in one entry are queued and shown sequentially (one
  toast at a time, FIFO).
- `goal_reached` copy: "Goal reached! You hit your target weight."
- Milestone copy: "{N} lb milestone reached!" where N is the threshold value.
- The user can dismiss early via a close action on the Alert.

## Rationale

**Toast vs modal:** A modal requires explicit dismissal and blocks interaction —
appropriate for a major once-in-a-lifetime event but intrusive for a routine
5 lb milestone.  A toast is lower interruption and works equally well for both
achievement types with contextual copy.  One component with distinct copy covers
both `goal_reached` and `milestone` types.

**6-second auto-hide:** Long enough to read, short enough not to block the
navigation back to /weight.  Navigation is delayed until all toasts in the queue
are dismissed (or auto-hide), giving users time to see each achievement.

**Reduced motion:** `window.matchMedia('(prefers-reduced-motion: reduce)')`
is the WCAG 2.1 AA-required mechanism for disabling animations (NFR-A-6).
Disabling the Slide transition meets the requirement.

## Impact

- `WeightEntryFormPage.tsx` — renders `AchievementNotification`; delays
  navigation to `/weight` until the toast queue is empty.
- `AchievementNotification.tsx` — new component consuming
  `AchievementRecord[]` from the weight-entry create response.

## Visual Reference

MUI Snackbar positioned `anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}`.
Alert severity `success`.  Close button via Alert's built-in `onClose` prop.
