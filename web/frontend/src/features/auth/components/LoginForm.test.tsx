import { ThemeProvider } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { theme } from '../../../theme/theme';
import { LoginForm } from './LoginForm';

function Wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (
    <MemoryRouter>
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={qc}>{children}</QueryClientProvider>
      </ThemeProvider>
    </MemoryRouter>
  );
}

describe('LoginForm', () => {
  it('renders email and password fields and a submit button', () => {
    render(
      <Wrapper>
        <LoginForm onSubmit={vi.fn()} status="idle" />
      </Wrapper>,
    );
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /log in/i })).toBeInTheDocument();
  });

  it('shows a client-side validation error for invalid email', async () => {
    render(
      <Wrapper>
        <LoginForm onSubmit={vi.fn()} status="idle" />
      </Wrapper>,
    );
    await userEvent.type(screen.getByLabelText(/email/i), 'not-an-email');
    await userEvent.click(screen.getByRole('button', { name: /log in/i }));
    expect(await screen.findByText(/enter a valid email address/i)).toBeInTheDocument();
  });

  it('calls onSubmit with form values when valid', async () => {
    const onSubmit = vi.fn();
    render(
      <Wrapper>
        <LoginForm onSubmit={onSubmit} status="idle" />
      </Wrapper>,
    );
    await userEvent.type(screen.getByLabelText(/email/i), 'jane@example.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'Aa1!aaaaaaaa');
    await userEvent.click(screen.getByRole('button', { name: /log in/i }));
    await waitFor(() =>
      expect(onSubmit).toHaveBeenCalledWith(
        { email: 'jane@example.com', password: 'Aa1!aaaaaaaa' },
        expect.objectContaining({
          setError: expect.any(Function),
          resetField: expect.any(Function),
        }),
      ),
    );
  });

  it('renders a form-level alert for the formError prop', () => {
    render(
      <Wrapper>
        <LoginForm onSubmit={vi.fn()} status="idle" formError="Invalid credentials." />
      </Wrapper>,
    );
    const alert = screen.getByRole('alert');
    expect(alert).toHaveTextContent(/invalid credentials/i);
  });

  it('disables the submit button while submitting', () => {
    render(
      <Wrapper>
        <LoginForm onSubmit={vi.fn()} status="submitting" />
      </Wrapper>,
    );
    expect(screen.getByRole('button', { name: /log in/i })).toBeDisabled();
  });
});
