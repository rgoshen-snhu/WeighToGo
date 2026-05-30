import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';

import type { TrendPointResponse } from '../api/dashboard-client';
import { WeightTrendChart } from './WeightTrendChart';

/** Build a trend point `daysAgo` days before 2026-05-29. */
function point(daysAgo: number, value: number): TrendPointResponse {
  const base = new Date('2026-05-29T00:00:00Z');
  base.setUTCDate(base.getUTCDate() - daysAgo);
  return {
    observation_date: base.toISOString().slice(0, 10),
    weight_value: value,
    weight_unit: 'lbs',
  };
}

const series: TrendPointResponse[] = [
  point(60, 200),
  point(45, 195),
  point(20, 190),
  point(5, 185),
  point(1, 183),
];

describe('WeightTrendChart', () => {
  it('renders a range selector group with four options', () => {
    render(<WeightTrendChart trend={series} today="2026-05-29" />);
    const group = screen.getByRole('group', { name: /trend range/i });
    expect(within(group).getByRole('button', { name: /7 days/i })).toBeInTheDocument();
    expect(within(group).getByRole('button', { name: /30 days/i })).toBeInTheDocument();
    expect(within(group).getByRole('button', { name: /90 days/i })).toBeInTheDocument();
    expect(within(group).getByRole('button', { name: /all/i })).toBeInTheDocument();
  });

  it('renders an accessible data table alternative mirroring the series', () => {
    render(<WeightTrendChart trend={series} today="2026-05-29" />);
    const table = screen.getByRole('table', { name: /weight trend/i });
    // header row + one row per point in the default (All) range
    const rows = within(table).getAllByRole('row');
    expect(rows).toHaveLength(series.length + 1);
  });

  it('renders an empty state when there is no data', () => {
    render(<WeightTrendChart trend={[]} today="2026-05-29" />);
    expect(screen.getByText(/no trend data yet/i)).toBeInTheDocument();
  });

  it('filters the table to the last 7 days when the 7-day range is selected', async () => {
    const user = userEvent.setup();
    render(<WeightTrendChart trend={series} today="2026-05-29" />);
    await user.click(screen.getByRole('button', { name: /7 days/i }));
    const table = screen.getByRole('table', { name: /weight trend/i });
    const rows = within(table).getAllByRole('row');
    // only the points at 5 and 1 days ago fall within 7 days -> 2 data rows + header
    expect(rows).toHaveLength(3);
  });

  it('exposes an accessible name for the chart region', () => {
    render(<WeightTrendChart trend={series} today="2026-05-29" />);
    expect(screen.getByRole('figure', { name: /weight trend/i })).toBeInTheDocument();
  });

  it('shows loading text while loading', () => {
    render(<WeightTrendChart trend={[]} today="2026-05-29" isLoading />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('shows an error message on error', () => {
    render(<WeightTrendChart trend={[]} today="2026-05-29" isError />);
    expect(screen.getByText(/failed to load/i)).toBeInTheDocument();
  });

  it('names the chart region with the series unit for screen readers', () => {
    render(<WeightTrendChart trend={series} today="2026-05-29" />);
    expect(
      screen.getByRole('figure', { name: /weight trend over time, measured in lbs/i }),
    ).toBeInTheDocument();
  });

  it('names the chart region with a kg unit when the series is in kg', () => {
    const kgSeries: TrendPointResponse[] = [
      { observation_date: '2026-05-20', weight_value: 80, weight_unit: 'kg' },
    ];
    render(<WeightTrendChart trend={kgSeries} today="2026-05-29" />);
    expect(screen.getByRole('figure', { name: /measured in kg/i })).toBeInTheDocument();
  });

  it('formats the table weight values with one decimal and the unit', () => {
    // 175 raw would render "175 lbs"; formatWeight renders "175.0 lbs".
    const single: TrendPointResponse[] = [
      { observation_date: '2026-05-20', weight_value: 175, weight_unit: 'lbs' },
    ];
    render(<WeightTrendChart trend={single} today="2026-05-29" />);
    const table = screen.getByRole('table', { name: /weight trend/i });
    expect(within(table).getByText('175.0 lbs')).toBeInTheDocument();
  });
});
