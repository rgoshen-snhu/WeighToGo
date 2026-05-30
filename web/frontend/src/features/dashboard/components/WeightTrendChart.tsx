import { useMemo, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
  useTheme,
} from '@mui/material';
import { visuallyHidden } from '@mui/utils';
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { TrendPointResponse } from '../api/dashboard-client';
import { formatObservationDate, formatWeight } from '../../../lib/format';
import type { Preferences } from '../../../contexts/PreferencesContext';

/** Selectable trend ranges (FR-D-2). `all` shows the full series. */
type Range = '7' | '30' | '90' | 'all';

const RANGE_OPTIONS: ReadonlyArray<{ value: Range; label: string }> = [
  { value: '7', label: '7 days' },
  { value: '30', label: '30 days' },
  { value: '90', label: '90 days' },
  { value: 'all', label: 'All' },
];

interface WeightTrendChartProps {
  /** Full weight series, oldest first (FR-D-2). */
  trend: TrendPointResponse[];
  /**
   * Reference date (ISO yyyy-mm-dd) the ranges count back from. Defaults to the
   * current date; passed explicitly by tests for determinism.
   */
  today?: string;
  /** Whether the dashboard summary query is loading. */
  isLoading?: boolean;
  /** Whether the dashboard summary query errored. */
  isError?: boolean;
}

/** Return the inclusive lower-bound date string for a range, or null for `all`. */
function rangeFloor(range: Range, today: string): string | null {
  if (range === 'all') return null;
  const floor = new Date(`${today}T00:00:00Z`);
  floor.setUTCDate(floor.getUTCDate() - Number(range));
  return floor.toISOString().slice(0, 10);
}

/**
 * Weight trend line chart with a 7/30/90/all range selector (FR-D-2).
 *
 * Accessibility (DDR-0006, NFR-A-3): the visual Recharts line chart is paired
 * with a visually-hidden data table that mirrors the selected series, so screen
 * reader users perceive the same data sighted users see. The chart region
 * carries an accessible name via `role="figure"` and `aria-label`, and the
 * Y-axis is labelled with the series unit. The line uses the theme primary
 * colour, on which DDR-0006 bases its NFR-A-4 contrast claim.
 */
export function WeightTrendChart({
  trend,
  today,
  isLoading = false,
  isError = false,
}: WeightTrendChartProps) {
  const theme = useTheme();
  const referenceDate = today ?? new Date().toISOString().slice(0, 10);
  const [range, setRange] = useState<Range>('all');

  const visible = useMemo(() => {
    const floor = rangeFloor(range, referenceDate);
    if (floor === null) return trend;
    return trend.filter((p) => p.observation_date >= floor);
  }, [trend, range, referenceDate]);

  // The series is uniformly lbs from the backend; fall back to lbs when empty.
  const unit = trend[0]?.weight_unit ?? 'lbs';
  const axisLabel = `Weight (${unit})`;

  return (
    <Card>
      <CardContent>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 1,
          }}
        >
          <Typography variant="subtitle2" color="text.secondary">
            Weight Trend
          </Typography>
          <ToggleButtonGroup
            size="small"
            exclusive
            value={range}
            onChange={(_e, next: Range | null) => {
              if (next !== null) setRange(next);
            }}
            aria-label="Trend range"
          >
            {RANGE_OPTIONS.map((opt) => (
              <ToggleButton key={opt.value} value={opt.value}>
                {opt.label}
              </ToggleButton>
            ))}
          </ToggleButtonGroup>
        </Box>

        {isLoading ? (
          <Typography variant="body2" color="text.secondary">
            Loading…
          </Typography>
        ) : isError ? (
          <Typography variant="body2" color="error">
            Failed to load trend data.
          </Typography>
        ) : trend.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No trend data yet.
          </Typography>
        ) : (
          <Box role="figure" aria-label={`Weight trend over time, measured in ${unit}`}>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={visible} title="Weight trend over time">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="observation_date" />
                <YAxis label={{ value: axisLabel, angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="weight_value"
                  stroke={theme.palette.primary.main}
                  dot={false}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>

            <Box component="table" sx={visuallyHidden} aria-label="Weight trend data">
              <caption>Weight trend over the selected range</caption>
              <thead>
                <tr>
                  <th scope="col">Date</th>
                  <th scope="col">Weight</th>
                </tr>
              </thead>
              <tbody>
                {visible.map((p) => (
                  <tr key={p.observation_date}>
                    <td>{formatObservationDate(p.observation_date)}</td>
                    <td>
                      {formatWeight(
                        Number(p.weight_value),
                        p.weight_unit as Preferences['weightUnit'],
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
