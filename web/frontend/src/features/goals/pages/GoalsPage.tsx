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
import { GoalProgressBar } from '../components/GoalProgressBar';
import { useActiveGoal } from '../hooks/useActiveGoal';
import { useAbandonGoal } from '../hooks/useAbandonGoal';
import { useSetGoal } from '../hooks/useSetGoal';
import { useUpdateGoal } from '../hooks/useUpdateGoal';
import type { GoalFormValues } from '../schemas/goal-schemas';

export function GoalsPage() {
  const { data, isLoading, isError } = useActiveGoal();
  const setGoal = useSetGoal();
  const updateGoal = useUpdateGoal();
  const abandonGoal = useAbandonGoal();

  const [isEditing, setIsEditing] = useState(false);
  const [conflictError, setConflictError] = useState<string | null>(null);

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
      }
    }
  }

  async function handleUpdate(values: GoalFormValues) {
    if (!activeGoal) return;
    await updateGoal.mutateAsync({
      goalId: activeGoal.goal_id,
      payload: {
        target_value: values.target_value,
        target_date: values.target_date || null,
      },
    });
    setIsEditing(false);
  }

  async function handleAbandon() {
    if (!activeGoal) return;
    await abandonGoal.mutateAsync(activeGoal.goal_id);
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
        <GoalFormWithPrefill onSubmit={handleCreate} conflictError={conflictError} />
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

      <Card>
        <CardContent>
          <Typography variant="subtitle2" color="text.secondary">
            {activeGoal.goal_type === 'lose' ? 'Lose weight' : 'Gain weight'}
          </Typography>
          <Typography variant="h5">
            {activeGoal.start_value} → {activeGoal.target_value} {activeGoal.target_unit}
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
    </Box>
  );
}

/**
 * GoalForm wrapper that pre-populates start_value from the latest weight entry.
 */
function GoalFormWithPrefill({
  onSubmit,
  conflictError,
}: {
  onSubmit: (values: GoalFormValues) => void;
  conflictError: string | null;
}) {
  const [defaultStartValue, setDefaultStartValue] = useState<number | undefined>(undefined);

  useEffect(() => {
    weightClient
      .list({ limit: 1 })
      .then((page) => {
        if (page.items[0]) {
          setDefaultStartValue(page.items[0].weight_value);
        }
      })
      .catch(() => {
        // No entries — start_value stays undefined for manual entry
      });
  }, []);

  return (
    <GoalForm
      onSubmit={onSubmit}
      conflictError={conflictError}
      defaultValues={{
        goal_type: 'lose',
        target_unit: 'lbs',
        start_value: defaultStartValue,
      }}
    />
  );
}
