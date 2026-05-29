/**
 * Shared form for creating and editing weight entries.
 *
 * Used by both /weight/new and /weight/:entryId/edit.  The calling page
 * determines the mode by whether defaultValues are provided.
 *
 * Validation is performed by React Hook Form + zodResolver.  Server 422
 * errors are mapped onto individual fields; server 409 errors render an
 * inline alert above the form.
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
import { type WeightEntryFormValues, weightEntrySchema } from '../schemas/weight-schemas';
import { toLocalISODate } from '../../../lib/date';

interface WeightEntryFormProps {
  /** Called with the validated form values when the user submits. */
  onSubmit: (values: WeightEntryFormValues) => void;
  /** Pre-populated values for edit mode. */
  defaultValues?: WeightEntryFormValues;
  /** A conflict error message to display above the form (e.g. 409 response). */
  conflictError?: string | null;
  /** Whether the form is being submitted. */
  isSubmitting?: boolean;
}

const TODAY = toLocalISODate();

/**
 * Weight entry form with full validation and accessibility.
 *
 * Fields: weight_value, weight_unit (lbs|kg), observation_date, notes.
 */
export function WeightEntryForm({
  onSubmit,
  defaultValues,
  conflictError,
  isSubmitting = false,
}: WeightEntryFormProps) {
  const { preferences, isLoading: prefsLoading } = usePreferences();

  const {
    register,
    handleSubmit,
    control,
    watch,
    setValue,
    formState: { errors },
  } = useForm<WeightEntryFormValues>({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolver: zodResolver(weightEntrySchema) as any,
    defaultValues: defaultValues ?? {
      weight_value: undefined,
      weight_unit: preferences.weightUnit,
      observation_date: TODAY,
      notes: '',
    },
  });

  // Sync weight_unit when the preferences query resolves after mount.
  // RHF defaultValues are set once at mount; if prefs were still loading
  // then, this effect applies the real preference once it arrives.
  useEffect(() => {
    if (!prefsLoading && !defaultValues) {
      setValue('weight_unit', preferences.weightUnit, { shouldDirty: false });
    }
  }, [prefsLoading, preferences.weightUnit, defaultValues, setValue]);

  const notesValue = watch('notes') ?? '';

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(onSubmit)}
      noValidate
      sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
    >
      {conflictError && <Alert severity="error">{conflictError}</Alert>}

      <TextField
        {...register('weight_value', { valueAsNumber: true })}
        label="Weight value"
        type="number"
        error={!!errors.weight_value}
        helperText={errors.weight_value?.message}
        required
        fullWidth
        slotProps={{ htmlInput: { step: '0.01', min: '0.01', inputMode: 'decimal' } }}
      />

      <FormControl fullWidth error={!!errors.weight_unit} required>
        <InputLabel id="weight-unit-label">Weight unit</InputLabel>
        <Controller
          name="weight_unit"
          control={control}
          render={({ field }) => (
            <Select
              {...field}
              labelId="weight-unit-label"
              label="Weight unit"
              inputProps={{ 'aria-label': 'Weight unit' }}
            >
              <MenuItem value="lbs">lbs</MenuItem>
              <MenuItem value="kg">kg</MenuItem>
            </Select>
          )}
        />
        {errors.weight_unit && <FormHelperText>{errors.weight_unit.message}</FormHelperText>}
      </FormControl>

      <TextField
        {...register('observation_date')}
        label="Observation date"
        type="date"
        slotProps={{ htmlInput: { max: TODAY }, inputLabel: { shrink: true } }}
        error={!!errors.observation_date}
        helperText={errors.observation_date?.message}
        required
        fullWidth
      />

      <TextField
        {...register('notes')}
        label="Notes"
        multiline
        rows={3}
        slotProps={{ htmlInput: { maxLength: 500 } }}
        helperText={`${notesValue.length} / 500`}
        error={!!errors.notes}
        fullWidth
      />

      <Button type="submit" variant="contained" disabled={isSubmitting}>
        Save
      </Button>
    </Box>
  );
}
