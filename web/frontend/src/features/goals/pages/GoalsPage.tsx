/**
 * Goals management page (/goals).
 *
 * States:
 * - Loading: shows spinner.
 * - No active goal: shows GoalForm to create one; start_value prefilled from
 *   the user's latest weight entry (fetched via GET /weight-entries?limit=1).
 * - Active goal: shows goal details, GoalProgressBar, and Edit / Abandon actions.
 * - Editing: GoalForm in edit mode for target_value / target_date.
 */

import { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  Stack,
  Typography,
} from '@mui/material';
import { weightClient } from '../../weight/api/weight-client';
import { ApiError } from '../../../lib/api-client';
import { GoalForm } from '../components/GoalForm';
import { GoalHistoryList } from '../components/GoalHistoryList';
import { GoalProgressBar } from '../components/GoalProgressBar';
import { useActiveGoal } from '../hooks/useActiveGoal';
import { useAbandonGoal } from '../hooks/useAbandonGoal';
import { useGoals } from '../hooks/useGoals';
import { useSetGoal } from '../hooks/useSetGoal';
import { useUpdateGoal } from '../hooks/useUpdateGoal';
import type { GoalFormValues } from '../schemas/goal-schemas';
import { usePreferences } from '../../../contexts/PreferencesContext';
import { formatWeightInPreferredUnit } from '../../../lib/format';
import type { WeightUnit } from '../../../lib/unit-conversion';

function mapError(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.status === 429) return 'Too many requests. Please wait a moment and try again.';
    if (err.status >= 500) return 'A server error occurred. Please try again.';
    return err.message || 'An unexpected error occurred.';
  }
  return 'An unexpected error occurred.';
}

export function GoalsPage() {
  const { data, isLoading, isError } = useActiveGoal();
  const setGoal = useSetGoal();
  const updateGoal = useUpdateGoal();
  const abandonGoal = useAbandonGoal();
  const goalHistory = useGoals({ history: true });
  const { preferences } = usePreferences();
  const preferredUnit = preferences.weightUnit;

  const [isEditing, setIsEditing] = useState(false);
  const [conflictError, setConflictError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const historySection = (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h6" component="h2" gutterBottom>
        Goal history
      </Typography>
      <GoalHistoryList goals={goalHistory.data?.goals ?? []} />
    </Box>
  );

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress aria-label="Loading goals" />
      </Box>
    );
  }

  if (isError) {
    return <Alert severity="error">Failed to load goal. Please refresh.</Alert>;
  }

  const activeGoal = data?.goal ?? null;

  async function handleCreate(values: GoalFormValues) {
    setConflictError(null);
    setActionError(null);
    try {
      await setGoal.mutateAsync({
        goal_type: values.goal_type,
        target_value: values.target_value,
        target_unit: values.target_unit,
        start_value: values.start_value,
        target_date: values.target_date || null,
      });
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setConflictError('You already have an active goal. Abandon it before creating a new one.');
      } else {
        setActionError(mapError(err));
      }
    }
  }

  async function handleUpdate(values: GoalFormValues) {
    if (!activeGoal) return;
    setActionError(null);
    try {
      await updateGoal.mutateAsync({
        goalId: activeGoal.goal_id,
        payload: {
          target_value: values.target_value,
          target_date: values.target_date || null,
        },
      });
      setIsEditing(false);
    } catch (err) {
      setActionError(mapError(err));
    }
  }

  async function handleAbandon() {
    if (!activeGoal) return;
    setActionError(null);
    try {
      await abandonGoal.mutateAsync(activeGoal.goal_id);
    } catch (err) {
      setActionError(mapError(err));
    }
  }

  // ── No active goal — show creation form ───────────────────────────────────

  if (!activeGoal) {
    return (
      <Box component="main" sx={{ maxWidth: 600, mx: 'auto', py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Goals
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Set a weight goal to track your progress over time.
        </Typography>
        {actionError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {actionError}
          </Alert>
        )}
        <GoalFormWithPrefill
          onSubmit={handleCreate}
          conflictError={conflictError}
          isSubmitting={setGoal.isPending}
          defaultUnit={preferredUnit}
        />
        {historySection}
      </Box>
    );
  }

  // ── Active goal — show details ─────────────────────────────────────────────

  if (isEditing) {
    return (
      <Box component="main" sx={{ maxWidth: 600, mx: 'auto', py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Edit Goal
        </Typography>
        {actionError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {actionError}
          </Alert>
        )}
        <GoalForm
          onSubmit={handleUpdate}
          isEditMode
          defaultValues={{
            goal_type: activeGoal.goal_type as 'lose' | 'gain',
            target_value: activeGoal.target_value,
            target_unit: activeGoal.target_unit as 'lbs' | 'kg',
            start_value: activeGoal.start_value,
            target_date: activeGoal.target_date ?? null,
          }}
          isSubmitting={updateGoal.isPending}
        />
        <Button sx={{ mt: 2 }} onClick={() => setIsEditing(false)}>
          Cancel
        </Button>
      </Box>
    );
  }

  return (
    <Box component="main" sx={{ maxWidth: 600, mx: 'auto', py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Goals
      </Typography>

      {actionError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {actionError}
        </Alert>
      )}

      <Card>
        <CardContent>
          <Typography variant="subtitle2" color="text.secondary">
            {activeGoal.goal_type === 'lose' ? 'Lose weight' : 'Gain weight'}
          </Typography>
          <Typography variant="h5">
            {formatWeightInPreferredUnit(
              activeGoal.start_value,
              activeGoal.target_unit as WeightUnit,
              preferredUnit,
            )}{' '}
            →{' '}
            {formatWeightInPreferredUnit(
              activeGoal.target_value,
              activeGoal.target_unit as WeightUnit,
              preferredUnit,
            )}
          </Typography>
          {activeGoal.target_date && (
            <Typography variant="body2" color="text.secondary">
              Target date: {activeGoal.target_date}
            </Typography>
          )}

          <Box sx={{ mt: 2 }}>
            <GoalProgressBar hasGoal={true} progressPercent={data?.progress_percent ?? null} />
          </Box>
        </CardContent>

        <Divider />

        <CardContent>
          <Stack direction="row" spacing={2}>
            <Button variant="outlined" onClick={() => setIsEditing(true)}>
              Edit goal
            </Button>
            <Button
              variant="outlined"
              color="error"
              onClick={handleAbandon}
              disabled={abandonGoal.isPending}
            >
              Abandon goal
            </Button>
          </Stack>
        </CardContent>
      </Card>

      {historySection}
    </Box>
  );
}

/**
 * GoalForm wrapper that pre-populates start_value and target_unit from the
 * latest weight entry. Defers rendering the form until the prefetch resolves
 * so that RHF's defaultValues captures the prefilled values at mount time.
 */
function GoalFormWithPrefill({
  onSubmit,
  conflictError,
  isSubmitting,
  defaultUnit,
}: {
  onSubmit: (values: GoalFormValues) => void;
  conflictError: string | null;
  isSubmitting: boolean;
  defaultUnit: 'lbs' | 'kg';
}) {
  const [isPrefetching, setIsPrefetching] = useState(true);
  const [prefillValues, setPrefillValues] = useState<Partial<GoalFormValues>>({
    goal_type: 'lose',
    // Use the user's preferred unit when there is no latest entry to infer from.
    target_unit: defaultUnit,
  });

  useEffect(() => {
    weightClient
      .list({ limit: 1 })
      .then((page) => {
        if (page.items[0]) {
          const entry = page.items[0];
          setPrefillValues({
            goal_type: 'lose',
            target_unit: entry.weight_unit as 'lbs' | 'kg',
            start_value: entry.weight_value,
          });
        }
      })
      .catch(() => {
        // No entries — form renders with manual-entry defaults
      })
      .finally(() => {
        setIsPrefetching(false);
      });
  }, []);

  if (isPrefetching) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress size={24} aria-label="Loading your latest weight" />
      </Box>
    );
  }

  return (
    <GoalForm
      onSubmit={onSubmit}
      conflictError={conflictError}
      defaultValues={prefillValues}
      isSubmitting={isSubmitting}
    />
  );
}
