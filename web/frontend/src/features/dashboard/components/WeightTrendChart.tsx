import { useMemo, useState } from 'react';
import { Box, Card, CardContent, ToggleButton, ToggleButtonGroup, Typography } from '@mui/material';
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
import { formatObservationDate } from '../../../lib/format';

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
 * carries an accessible name via `role="figure"` and `aria-label`.
 */
export function WeightTrendChart({ trend, today }: WeightTrendChartProps) {
  const referenceDate = today ?? new Date().toISOString().slice(0, 10);
  const [range, setRange] = useState<Range>('all');

  const visible = useMemo(() => {
    const floor = rangeFloor(range, referenceDate);
    if (floor === null) return trend;
    return trend.filter((p) => p.observation_date >= floor);
  }, [trend, range, referenceDate]);

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

        {trend.length === 0 ? (
          <Typography variant="body2" color="text.secondary">
            No trend data yet.
          </Typography>
        ) : (
          <Box role="figure" aria-label="Weight trend over time">
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={visible} title="Weight trend over time">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="observation_date" />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="weight_value"
                  stroke="currentColor"
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
                      {p.weight_value} {p.weight_unit}
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
