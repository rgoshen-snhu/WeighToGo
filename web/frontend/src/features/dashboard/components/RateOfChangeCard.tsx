import { Card, CardContent, Typography } from '@mui/material';
import type { RateOfChangeResponse } from '../api/dashboard-client';
import { formatWeight } from '../../../lib/format';
import { usePreferences, type Preferences } from '../../../contexts/PreferencesContext';
import { convertWeight, type WeightUnit } from '../../../lib/unit-conversion';

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
/** A recognised weight unit, or null when the backend omits one. */
function asWeightUnit(unit: string | null): WeightUnit | null {
  return unit === 'lbs' || unit === 'kg' ? unit : null;
}

export function RateOfChangeCard({ rateOfChange, isLoading, isError }: RateOfChangeCardProps) {
  const { preferences } = usePreferences();
  const preferredUnit = preferences.weightUnit;

  // Convert the backend rate (a delta, in its reported unit) into the user's
  // preferred unit. Conversion is multiplicative and offset-free, so it applies
  // to a delta exactly as to an absolute weight. When the backend reports no
  // unit, leave the magnitude unconverted and show it without a unit suffix
  // rather than guessing.
  let displayRate = rateOfChange?.weekly_rate ?? null;
  let displayUnit = '';
  if (rateOfChange != null && rateOfChange.weekly_rate != null) {
    const fromUnit = asWeightUnit(rateOfChange.unit);
    if (fromUnit != null) {
      displayRate = convertWeight(rateOfChange.weekly_rate, fromUnit, preferredUnit);
      displayUnit = preferredUnit;
    }
  }

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
        ) : rateOfChange == null || displayRate == null ? (
          <Typography variant="body2" color="text.secondary">
            Not enough data yet.
          </Typography>
        ) : (
          <RateValue rate={displayRate} unit={displayUnit} />
        )}
      </CardContent>
    </Card>
  );
}

function RateValue({ rate, unit }: { rate: number; unit: string }) {
  // A rate that rounds to 0.0 at the one-decimal display precision is shown as
  // "no change" rather than a misleading "Down 0.0 …". The threshold is applied
  // to the already-converted magnitude so "no change" is unit-consistent.
  if (Math.abs(rate) < 0.05) {
    return <Typography variant="h5">No change this week</Typography>;
  }

  // When the backend omits a unit, show the bare magnitude with no suffix and,
  // crucially, no dangling space where the unit would have gone. `formatWeight`
  // always appends "<space><unit>", which leaves a trailing space for an empty
  // unit, so format the magnitude directly in that case.
  const magnitude = unit
    ? formatWeight(Math.abs(rate), unit as Preferences['weightUnit'])
    : Math.abs(rate).toFixed(1);
  const direction = rate < 0 ? 'Down' : 'Up';

  return (
    <Typography variant="h5">
      {direction} {magnitude} / week
    </Typography>
  );
}
