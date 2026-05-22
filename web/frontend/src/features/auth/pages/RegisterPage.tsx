/**
 * Registration page stub.
 *
 * The registration form (display name, email, password, confirm password,
 * validation, API call) is implemented in Phase 6.
 *
 * Requirements: SRS §3.1 FR-03.
 */

import { Typography } from '@mui/material';
import { AuthLayout } from '../../../components/AuthLayout';

/**
 * Placeholder registration page rendered at /register.
 */
export function RegisterPage() {
  return (
    <AuthLayout>
      <Typography variant="h5" component="h1" gutterBottom>
        Create Account
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Registration form is implemented in Phase 6.
      </Typography>
    </AuthLayout>
  );
}
