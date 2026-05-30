/**
 * Dashboard page (FR-D-1).
 *
 * Displays a summary of the user's weight tracking progress.  When the user
 * has no entries, a full-width empty state with a CTA is shown instead.
 * Loading states use MUI Skeleton via the individual card components.
 */

import { Box, Button, Grid, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { EmptyState } from '../../../components/EmptyState';
import { GoalProgressCard } from '../components/GoalProgressCard';
import { LatestEntryCard } from '../components/LatestEntryCard';
import { RateOfChangeCard } from '../components/RateOfChangeCard';
import { TotalEntriesCard } from '../components/TotalEntriesCard';
import { WeightTrendChart } from '../components/WeightTrendChart';
import { useDashboardSummary } from '../hooks/useDashboardSummary';

/**
 * Dashboard landing page rendered at /.
 */
export function DashboardPage() {
  const { data, isLoading, isError } = useDashboardSummary();

  const isEmpty = !isLoading && data !== undefined && data.total_entries === 0 && !data.active_goal;

  return (
    <Box component="main">
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>

      {isEmpty ? (
        <EmptyState
          title="No entries yet"
          description="Start tracking your progress by logging your first weight entry."
          action={
            <Button component={RouterLink} to="/weight/new" variant="contained">
              Add your first entry
            </Button>
          }
        />
      ) : (
        <Grid container spacing={3}>
          <Grid size={{ xs: 12, sm: 4 }}>
            <LatestEntryCard entry={data?.latest_entry} isLoading={isLoading} />
          </Grid>
          <Grid size={{ xs: 12, sm: 4 }}>
            <TotalEntriesCard total={data?.total_entries ?? 0} isLoading={isLoading} />
          </Grid>
          <Grid size={{ xs: 12, sm: 4 }}>
            <GoalProgressCard
              activeGoal={data?.active_goal ?? null}
              isLoading={isLoading}
              isError={isError}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 4 }}>
            <RateOfChangeCard
              rateOfChange={data?.rate_of_change}
              isLoading={isLoading}
              isError={isError}
            />
          </Grid>
          <Grid size={{ xs: 12 }}>
            <WeightTrendChart trend={data?.trend ?? []} isLoading={isLoading} isError={isError} />
          </Grid>
        </Grid>
      )}
    </Box>
  );
}
