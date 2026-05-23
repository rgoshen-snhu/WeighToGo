import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import type { UseFormSetError } from 'react-hook-form';
import { useAuth } from '../../../contexts/AuthContext';
import { authClient, type AuthUser } from '../api/auth-client';
import { ApiError, ValidationError } from '../../../lib/api-client';
import type { LoginFormValues } from '../schemas/auth-schemas';

export function useLogin() {
  const { setUser } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [formError, setFormError] = useState<string | null>(null);

  const mutation = useMutation<
    AuthUser,
    Error,
    { values: LoginFormValues; setError: UseFormSetError<LoginFormValues> }
  >({
    mutationFn: ({ values }) => authClient.login(values),
    onSuccess: (user) => {
      setUser(user);
      const dest = searchParams.get('from') ?? '/';
      navigate(dest, { replace: true });
    },
    onError: (error, vars) => {
      if (error instanceof ValidationError) {
        for (const [field, message] of Object.entries(error.fieldErrors)) {
          vars.setError(field as keyof LoginFormValues, { type: 'server', message });
        }
        return;
      }
      if (error instanceof ApiError) {
        if (error.status === 401) setFormError('Invalid credentials.');
        else if (error.status === 423)
          setFormError('Account is temporarily locked. Please try again later.');
        else if (error.status === 429)
          setFormError('Too many attempts. Please wait a moment and try again.');
        else setFormError('Something went wrong. Please try again.');
      } else {
        setFormError('Something went wrong. Please try again.');
      }
    },
  });

  return {
    submit: (values: LoginFormValues, setError: UseFormSetError<LoginFormValues>) => {
      setFormError(null);
      mutation.mutate({ values, setError });
    },
    status: mutation.isPending ? ('submitting' as const) : ('idle' as const),
    formError,
  };
}
