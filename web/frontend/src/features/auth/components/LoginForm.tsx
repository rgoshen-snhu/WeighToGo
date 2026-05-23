import { zodResolver } from '@hookform/resolvers/zod';
import { Alert, Box, Button, Stack, TextField } from '@mui/material';
import { useForm, type UseFormResetField, type UseFormSetError } from 'react-hook-form';
import { loginSchema, type LoginFormValues } from '../schemas/auth-schemas';

export type LoginFormStatus = 'idle' | 'submitting';

/** Helpers from react-hook-form forwarded to the onSubmit callback. */
export interface LoginFormHelpers {
  setError: UseFormSetError<LoginFormValues>;
  resetField: UseFormResetField<LoginFormValues>;
}

export interface LoginFormProps {
  onSubmit: (values: LoginFormValues, helpers: LoginFormHelpers) => void | Promise<void>;
  status: LoginFormStatus;
  formError?: string | null;
}

/**
 * Login form with client-side validation via Zod + React Hook Form.
 *
 * Validates email format and password presence before calling `onSubmit`.
 * The parent supplies status and any server-level error to render as a
 * form-level alert.
 *
 * Requirements: SRS §3.1 FR-01.
 */
export function LoginForm({ onSubmit, status, formError }: LoginFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
    resetField,
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    mode: 'onSubmit',
    reValidateMode: 'onBlur',
  });

  return (
    <Box
      component="form"
      noValidate
      onSubmit={handleSubmit((v) => onSubmit(v, { setError, resetField }))}
    >
      <Box aria-live="polite" sx={{ mb: formError ? 2 : 0 }}>
        {formError && (
          <Alert severity="error" role="alert">
            {formError}
          </Alert>
        )}
      </Box>
      <Stack spacing={2}>
        <TextField
          label="Email"
          type="email"
          autoComplete="email"
          fullWidth
          error={!!errors.email}
          helperText={errors.email?.message}
          {...register('email')}
        />
        <TextField
          label="Password"
          type="password"
          autoComplete="current-password"
          fullWidth
          error={!!errors.password}
          helperText={errors.password?.message}
          {...register('password')}
        />
        <Button type="submit" variant="contained" disabled={status === 'submitting'} fullWidth>
          Log in
        </Button>
      </Stack>
    </Box>
  );
}
