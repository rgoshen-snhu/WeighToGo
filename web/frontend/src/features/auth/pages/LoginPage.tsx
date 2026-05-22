/**
 * Login page stub.
 *
 * The auth form UI (email/password fields, validation, API call) is
 * implemented in Phase 6. This stub exists so the router has a renderable
 * component for the /login route.
 *
 * Requirements: SRS §3.1 FR-01, FR-02.
 */

import { Typography } from '@mui/material';
import { AuthLayout } from '../../../components/AuthLayout';

/**
 * Placeholder login page rendered at /login.
 */
export function LoginPage() {
  return (
    <AuthLayout>
      <Typography variant="h5" component="h1" gutterBottom>
        Log In
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Sign-in form is implemented in Phase 6.
      </Typography>
    </AuthLayout>
  );
}
