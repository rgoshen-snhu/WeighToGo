/**
 * Registration page.
 *
 * Composes AuthLayout, RegisterForm, and useRegister to provide a fully wired
 * registration screen. Redirects authenticated users immediately to the app root.
 *
 * Requirements: SRS §6.1 FR-A-1, FR-A-5.
 */

import { Typography } from '@mui/material';
import { Navigate } from 'react-router-dom';
import { AuthLayout } from '../../../components/AuthLayout';
import { useAuth } from '../../../contexts/AuthContext';
import { RegisterForm } from '../components/RegisterForm';
import { useRegister } from '../hooks/useRegister';

/**
 * Renders the registration page at /register.
 */
export function RegisterPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const { submit, status, formError } = useRegister();

  if (isLoading) return null;
  if (isAuthenticated) return <Navigate to="/" replace />;

  return (
    <AuthLayout>
      <Typography variant="h5" component="h2" gutterBottom>
        Create Account
      </Typography>
      <RegisterForm onSubmit={submit} status={status} formError={formError} />
    </AuthLayout>
  );
}
