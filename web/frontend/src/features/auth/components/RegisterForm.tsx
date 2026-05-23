import { zodResolver } from '@hookform/resolvers/zod';
import { Alert, Box, Button, Stack, TextField } from '@mui/material';
import { useForm, type UseFormSetError } from 'react-hook-form';
import { registerSchema, type RegisterFormValues } from '../schemas/auth-schemas';

export interface RegisterFormProps {
  onSubmit: (
    values: RegisterFormValues,
    setError: UseFormSetError<RegisterFormValues>,
  ) => void | Promise<void>;
  status: 'idle' | 'submitting';
  formError?: string | null;
}

/**
 * Registration form with client-side validation via Zod + React Hook Form.
 *
 * Validates display name, email, password complexity (≥12 chars, mixed case,
 * digit, special character), and confirm-password equality before calling
 * `onSubmit`. The parent supplies status and any server-level error to render
 * as a form-level alert.
 *
 * Requirements: SRS §3.1 FR-03.
 */
export function RegisterForm({ onSubmit, status, formError }: RegisterFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    mode: 'onSubmit',
    reValidateMode: 'onBlur',
    shouldFocusError: true,
  });

  return (
    <Box component="form" noValidate onSubmit={handleSubmit((v) => onSubmit(v, setError))}>
      <Box aria-live="polite" sx={{ mb: formError ? 2 : 0 }}>
        {formError && (
          <Alert severity="error" role="alert">
            {formError}
          </Alert>
        )}
      </Box>
      <Stack spacing={2}>
        <TextField
          label="Display name"
          fullWidth
          autoComplete="name"
          error={!!errors.displayName}
          helperText={errors.displayName?.message}
          {...register('displayName')}
        />
        <TextField
          label="Email"
          type="email"
          fullWidth
          autoComplete="email"
          error={!!errors.email}
          helperText={errors.email?.message}
          {...register('email')}
        />
        <TextField
          label="Password"
          type="password"
          fullWidth
          autoComplete="new-password"
          error={!!errors.password}
          helperText={errors.password?.message}
          {...register('password')}
        />
        <TextField
          label="Confirm password"
          type="password"
          fullWidth
          autoComplete="new-password"
          error={!!errors.confirmPassword}
          helperText={errors.confirmPassword?.message}
          {...register('confirmPassword')}
        />
        <Button type="submit" variant="contained" disabled={status === 'submitting'} fullWidth>
          Create account
        </Button>
      </Stack>
    </Box>
  );
}
