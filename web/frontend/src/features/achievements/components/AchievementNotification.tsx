/**
 * Achievement toast notification (FR-N-1, DDR-0007).
 *
 * Shows one Snackbar toast per achievement. Queue management lives in the
 * parent: when the current toast is dismissed, `onDismissOne` is called so the
 * parent can remove the first item from its list. When the list is empty no
 * toast is rendered.
 *
 * role="status" provides a polite ARIA live region (NFR-A-3).
 * MUI honours prefers-reduced-motion on its internal transitions (NFR-A-6).
 */

import { Alert, Snackbar } from '@mui/material';
import { useCallback } from 'react';

import { parseThreshold, type AchievementRecord } from '../schemas/achievement';

interface Props {
  /** Achievements queue — the first element is the one currently displayed. */
  achievements: AchievementRecord[];
  /** Called when the current (first) toast is dismissed. */
  onDismissOne: () => void;
}

function toastMessage(ach: AchievementRecord): string {
  if (ach.achievement_type === 'goal_reached') {
    return 'Goal reached! You hit your target weight.';
  }
  // parseThreshold strips trailing zeros from the Numeric(6,2) serialised
  // string and guards against a null/NaN value.
  const value = parseThreshold(ach.threshold);
  if (ach.achievement_type === 'streak') {
    return value === null
      ? 'Logging streak! Keep it up.'
      : `${value}-day logging streak! Keep it up.`;
  }
  return value === null ? 'Milestone reached!' : `${value} lb milestone reached!`;
}

export function AchievementNotification({ achievements, onDismissOne }: Props) {
  const handleClose = useCallback(() => onDismissOne(), [onDismissOne]);

  const current = achievements[0];
  if (current === undefined) return null;

  return (
    <Snackbar
      key={current.achievement_id}
      open
      autoHideDuration={6000}
      onClose={handleClose}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
    >
      <Alert role="status" severity="success" onClose={handleClose} sx={{ width: '100%' }}>
        {toastMessage(current)}
      </Alert>
    </Snackbar>
  );
}
