import { Card, CardContent, Typography } from '@mui/material';
import type { RateOfChangeResponse } from '../api/dashboard-client';
import { formatWeight } from '../../../lib/format';
import type { Preferences } from '../../../contexts/PreferencesContext';

interface RateOfChangeCardProps {
  /** Rate-of-change figure from the dashboard summary, or undefined while pending. */
  rateOfChange: RateOfChangeResponse | undefined;
  /** Whether the dashboard summary query is loading. */
  isLoading: boolean;
  /** Whether the dashboard summary query errored. */
  isError: boolean;
}

/**
 * Dashboard card showing the user's weekly rate of weight change (FR-D-3).
 *
 * Mirrors the GoalProgressCard loading/error/data state pattern. When the
 * backend reports insufficient data (`weekly_rate` is null), an explicit
 * "Not enough data yet" message is shown rather than a misleading zero.
 */
export function RateOfChangeCard({ rateOfChange, isLoading, isError }: RateOfChangeCardProps) {
  return (
    <Card>
      <CardContent>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          Rate of Change
        </Typography>
        {isLoading ? (
          <Typography variant="body2" color="text.secondary">
            Loading…
          </Typography>
        ) : isError ? (
          <Typography variant="body2" color="error">
            Failed to load rate of change.
          </Typography>
        ) : rateOfChange == null || rateOfChange.weekly_rate == null ? (
          <Typography variant="body2" color="text.secondary">
            Not enough data yet.
          </Typography>
        ) : (
          <RateValue rate={rateOfChange.weekly_rate} unit={rateOfChange.unit ?? ''} />
        )}
      </CardContent>
    </Card>
  );
}

function RateValue({ rate, unit }: { rate: number; unit: string }) {
  // A rate that rounds to 0.0 at the one-decimal display precision is shown as
  // "no change" rather than a misleading "Down 0.0 …".
  if (Math.abs(rate) < 0.05) {
    return <Typography variant="h5">No change this week</Typography>;
  }

  const magnitude = formatWeight(Math.abs(rate), unit as Preferences['weightUnit']);
  const direction = rate < 0 ? 'Down' : 'Up';

  return (
    <Typography variant="h5">
      {direction} {magnitude} / week
    </Typography>
  );
}
