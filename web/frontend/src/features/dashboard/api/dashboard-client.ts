/**
 * Typed wrapper around the GET /api/v1/dashboard/summary endpoint.
 */

import { fetchJson } from '../../../lib/api-client';
import type { ActiveGoalResponse } from '../../goals/api/goal-client';
import type { WeightEntryRecord } from '../../weight/api/weight-client';

const BASE = '/api/v1/dashboard';

/** Weekly rate-of-change figure from the dashboard summary (FR-D-3). */
export interface RateOfChangeResponse {
  /** Signed weight change per week, or null when there is insufficient data. */
  weekly_rate: number | null;
  /** Unit of `weekly_rate`, or null. */
  unit: string | null;
  /** Reason `weekly_rate` is null (e.g. "insufficient_data"), or null. */
  reason: string | null;
}

/** A single point in the weight trend series (FR-D-2). */
export interface TrendPointResponse {
  observation_date: string;
  weight_value: number;
  weight_unit: string;
}

/** Dashboard summary response from the API. */
export interface DashboardSummaryResponse {
  latest_entry: WeightEntryRecord | null;
  total_entries: number;
  active_goal: ActiveGoalResponse | null;
  rate_of_change: RateOfChangeResponse;
  trend: TrendPointResponse[];
}

/** Typed API wrapper for the dashboard summary endpoint. */
export const dashboardClient = {
  /** Return the dashboard summary for the current user. */
  summary: () => fetchJson<DashboardSummaryResponse>(`${BASE}/summary`, { method: 'GET' }),
};
