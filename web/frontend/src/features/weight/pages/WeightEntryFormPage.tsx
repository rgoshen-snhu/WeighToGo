/**
 * Weight entry create / edit page (FR-W-1, FR-W-3).
 *
 * Detects create vs edit mode from the route parameter.  In edit mode the
 * existing entry is fetched and the form is pre-populated.  On successful
 * submit the user is navigated back to /weight.
 */

import { Alert, Box, CircularProgress, Typography } from '@mui/material';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { AchievementNotification } from '../../achievements/components/AchievementNotification';
import { useVisibleAchievements } from '../../achievements/hooks/useVisibleAchievements';
import type { AchievementRecord } from '../../achievements/schemas/achievement';
import { ApiError, ValidationError } from '../../../lib/api-client';
import { WeightEntryForm } from '../components/WeightEntryForm';
import { useCreateWeightEntry } from '../hooks/useCreateWeightEntry';
import { useUpdateWeightEntry } from '../hooks/useUpdateWeightEntry';
import { useWeightEntry } from '../hooks/useWeightEntry';
import type { WeightEntryFormValues } from '../schemas/weight-schemas';

/**
 * Log-a-weight page rendered at /weight/new and /weight/:entryId/edit.
 */
export function WeightEntryFormPage() {
  const { entryId: entryIdStr } = useParams<{ entryId?: string }>();
  const navigate = useNavigate();
  const [conflictError, setConflictError] = useState<string | null>(null);

  const entryId =
    entryIdStr !== undefined
      ? Number.isNaN(Number(entryIdStr))
        ? null
        : Number(entryIdStr)
      : null;
  const isEditMode = entryId !== null;

  const {
    data: existingEntry,
    isLoading: isLoadingEntry,
    isError: entryFetchFailed,
  } = useWeightEntry(isEditMode ? entryId : null);

  const createMutation = useCreateWeightEntry();
  const updateMutation = useUpdateWeightEntry();
  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  const [newAchievements, setNewAchievements] = useState<AchievementRecord[]>([]);
  const visibleAchievements = useVisibleAchievements(newAchievements);
  const pendingNavRef = useRef(false);

  // Remove the displayed achievement (first visible) from the raw queue.
  // Slicing prev[0] would be wrong when hidden items precede the visible one:
  // closing the toast would remove a hidden item, leaving the same visible
  // achievement re-displayed on the next render.
  const handleDismissOne = useCallback(() => {
    const displayed = visibleAchievements[0];
    if (!displayed) return;
    setNewAchievements((prev) => prev.filter((a) => a.achievement_id !== displayed.achievement_id));
  }, [visibleAchievements]);

  // Navigate to /weight once the visible achievement queue drains (FR-N-1 DDR-0007).
  // visibleAchievements filters out suppressed types so navigation is not blocked
  // when the user has turned off a notification toggle.
  useEffect(() => {
    if (visibleAchievements.length === 0 && pendingNavRef.current) {
      pendingNavRef.current = false;
      void navigate('/weight');
    }
  }, [visibleAchievements.length, navigate]);

  const handleSubmit = (values: WeightEntryFormValues) => {
    setConflictError(null);
    const onError = (error: Error) => {
      if (error instanceof ValidationError || (error instanceof ApiError && error.status === 409)) {
        setConflictError('An entry already exists for this date. Edit the existing entry instead.');
      }
    };

    if (isEditMode) {
      updateMutation.mutate(
        { entryId, payload: values },
        { onSuccess: () => void navigate('/weight'), onError },
      );
    } else {
      createMutation.mutate(values, {
        onSuccess: (data) => {
          const earned = data.newly_earned_achievements ?? [];
          if (earned.length > 0) {
            setNewAchievements(earned);
            pendingNavRef.current = true;
          } else {
            void navigate('/weight');
          }
        },
        onError,
      });
    }
  };

  const title = isEditMode ? 'Edit Entry' : 'Log Weight';

  if (isEditMode && isLoadingEntry) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  // Non-numeric entryId in the URL (e.g. /weight/abc/edit), or the entry
  // could not be fetched (e.g. it was soft-deleted, never existed, or the
  // caller does not own it). Without this branch the form would render
  // blank and a PUT on submit would surface as 404 with no useful UI
  // (PR #30 review).
  if ((entryIdStr !== undefined && entryId === null) || entryFetchFailed) {
    return (
      <Box component="main">
        <Typography variant="h4" component="h1" gutterBottom>
          Not Found
        </Typography>
        <Alert severity="error">Entry not found.</Alert>
      </Box>
    );
  }

  const defaultValues =
    existingEntry !== undefined
      ? {
          weight_value: existingEntry.weight_value,
          weight_unit: existingEntry.weight_unit as 'lbs' | 'kg',
          observation_date: existingEntry.observation_date,
          notes: existingEntry.notes ?? undefined,
        }
      : undefined;

  return (
    <Box component="main" sx={{ maxWidth: 480, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        {title}
      </Typography>
      <WeightEntryForm
        onSubmit={handleSubmit}
        defaultValues={defaultValues}
        conflictError={conflictError}
        isSubmitting={isSubmitting}
      />
      <AchievementNotification achievements={visibleAchievements} onDismissOne={handleDismissOne} />
    </Box>
  );
}
