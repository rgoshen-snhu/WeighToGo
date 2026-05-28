/**
 * Login page.
 *
 * Composes AuthLayout, LoginForm, and useLogin to provide a fully wired
 * login screen. Redirects authenticated users immediately to the app root
 * (or to the ?from= destination if present).
 *
 * Requirements: SRS §6.1 FR-A-2, FR-A-5.
 */

import { Typography } from '@mui/material';
import { Navigate, useSearchParams } from 'react-router-dom';
import { AuthLayout } from '../../../components/AuthLayout';
import { useAuth } from '../../../contexts/AuthContext';
import { LoginForm } from '../components/LoginForm';
import { useLogin } from '../hooks/useLogin';

/**
 * Renders the login page at /login.
 */
export function LoginPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const { submit, status, formError } = useLogin();
  const [searchParams] = useSearchParams();

  if (isLoading) return null;
  // Redirect already-authenticated users to the ?from= destination (or the
  // dashboard).  Using the same destination as useLogin prevents a race where
  // the page re-renders with isAuthenticated=true after login and overrides the
  // navigate() call in useLogin.
  if (isAuthenticated) {
    const dest = searchParams.get('from') ?? '/';
    return <Navigate to={dest} replace />;
  }

  return (
    <AuthLayout>
      <Typography variant="h5" component="h2" gutterBottom>
        Log In
      </Typography>
      <LoginForm onSubmit={submit} status={status} formError={formError} />
    </AuthLayout>
  );
}
