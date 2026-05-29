/**
 * Form for creating or editing a weight goal.
 *
 * Create mode: all fields visible; start_value prefilled from latest entry.
 * Edit mode (editGoalId provided): only target_value and target_date are
 * editable per FR-G-3. goal_type and start_value are locked.
 */

import {
  Alert,
  Box,
  Button,
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Select,
  TextField,
} from '@mui/material';
import { zodResolver } from '@hookform/resolvers/zod';
import { useEffect } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { usePreferences } from '../../../contexts/PreferencesContext';
import { type GoalFormValues, goalFormSchema } from '../schemas/goal-schemas';

interface GoalFormProps {
  /** Called with validated form values on submit. */
  onSubmit: (values: GoalFormValues) => void;
  /** Pre-populated values (edit mode when provided). */
  defaultValues?: Partial<GoalFormValues>;
  /** Whether the form is in edit mode (locks goal_type and start_value). */
  isEditMode?: boolean;
  /** A 409 conflict error message to show above the form. */
  conflictError?: string | null;
  /** Whether the form is currently submitting. */
  isSubmitting?: boolean;
}

/**
 * Goal creation / update form with full validation and accessibility.
 */
export function GoalForm({
  onSubmit,
  defaultValues,
  isEditMode = false,
  conflictError,
  isSubmitting = false,
}: GoalFormProps) {
  const { preferences, isLoading: prefsLoading } = usePreferences();

  const {
    register,
    handleSubmit,
    control,
    setValue,
    formState: { errors },
  } = useForm<GoalFormValues>({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolver: zodResolver(goalFormSchema) as any,
    defaultValues: defaultValues ?? {
      goal_type: 'lose',
      target_value: undefined,
      target_unit: preferences.weightUnit,
      start_value: undefined,
      target_date: null,
    },
  });

  // Sync target_unit when the preferences query resolves after mount.
  useEffect(() => {
    if (!prefsLoading && !defaultValues) {
      setValue('target_unit', preferences.weightUnit, { shouldDirty: false });
    }
  }, [prefsLoading, preferences.weightUnit, defaultValues, setValue]);

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(onSubmit)}
      noValidate
      sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
    >
      {conflictError && <Alert severity="error">{conflictError}</Alert>}

      {/* Goal type — locked in edit mode */}
      <FormControl fullWidth error={!!errors.goal_type} required disabled={isEditMode}>
        <InputLabel id="goal-type-label">Goal type</InputLabel>
        <Controller
          name="goal_type"
          control={control}
          render={({ field }) => (
            <Select {...field} labelId="goal-type-label" label="Goal type">
              <MenuItem value="lose">Lose weight</MenuItem>
              <MenuItem value="gain">Gain weight</MenuItem>
            </Select>
          )}
        />
        {errors.goal_type && <FormHelperText>{errors.goal_type.message}</FormHelperText>}
      </FormControl>

      {/* Target value */}
      <TextField
        {...register('target_value', { valueAsNumber: true })}
        label="Target weight"
        type="number"
        error={!!errors.target_value}
        helperText={errors.target_value?.message}
        required
        fullWidth
        slotProps={{ htmlInput: { step: '0.01', min: '0.01', inputMode: 'decimal' } }}
      />

      {/* Weight unit — locked in edit mode */}
      <FormControl fullWidth error={!!errors.target_unit} required disabled={isEditMode}>
        <InputLabel id="target-unit-label">Weight unit</InputLabel>
        <Controller
          name="target_unit"
          control={control}
          render={({ field }) => (
            <Select {...field} labelId="target-unit-label" label="Weight unit">
              <MenuItem value="lbs">lbs</MenuItem>
              <MenuItem value="kg">kg</MenuItem>
            </Select>
          )}
        />
        {errors.target_unit && <FormHelperText>{errors.target_unit.message}</FormHelperText>}
      </FormControl>

      {/* Starting weight — locked in edit mode */}
      <TextField
        {...register('start_value', { valueAsNumber: true })}
        label="Starting weight"
        type="number"
        error={!!errors.start_value}
        helperText={
          errors.start_value?.message ?? (isEditMode ? 'Locked after goal creation.' : '')
        }
        required
        fullWidth
        disabled={isEditMode}
        slotProps={{ htmlInput: { step: '0.01', min: '0.01', inputMode: 'decimal' } }}
      />

      {/* Target date (optional) */}
      <TextField
        {...register('target_date')}
        label="Target date (optional)"
        type="date"
        error={!!errors.target_date}
        helperText={errors.target_date?.message}
        fullWidth
        slotProps={{ inputLabel: { shrink: true } }}
      />

      <Button type="submit" variant="contained" disabled={isSubmitting}>
        {isEditMode ? 'Update goal' : 'Set goal'}
      </Button>
    </Box>
  );
}
