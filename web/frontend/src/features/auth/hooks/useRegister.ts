import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { UseFormSetError } from 'react-hook-form';
import { useAuth } from '../../../contexts/AuthContext';
import { authClient, type AuthUser } from '../api/auth-client';
import { ApiError, ValidationError } from '../../../lib/api-client';
import type { RegisterFormValues } from '../schemas/auth-schemas';

export function useRegister() {
  const { setUser } = useAuth();
  const navigate = useNavigate();
  const [formError, setFormError] = useState<string | null>(null);

  const mutation = useMutation<
    AuthUser,
    Error,
    { values: RegisterFormValues; setError: UseFormSetError<RegisterFormValues> }
  >({
    mutationFn: ({ values }) =>
      authClient.register({
        email: values.email,
        password: values.password,
        displayName: values.displayName,
      }),
    onSuccess: (user) => {
      setUser(user);
      navigate('/', { replace: true });
    },
    onError: (error, vars) => {
      if (error instanceof ValidationError) {
        for (const [field, message] of Object.entries(error.fieldErrors)) {
          vars.setError(field as keyof RegisterFormValues, { type: 'server', message });
        }
        return;
      }
      if (error instanceof ApiError) {
        if (error.status === 409) setFormError('An account with this email already exists.');
        else setFormError('Something went wrong. Please try again.');
      } else {
        setFormError('Something went wrong. Please try again.');
      }
    },
  });

  return {
    submit: (values: RegisterFormValues, setError: UseFormSetError<RegisterFormValues>) => {
      setFormError(null);
      mutation.mutate({ values, setError });
    },
    status: mutation.isPending ? ('submitting' as const) : ('idle' as const),
    formError,
  };
}
