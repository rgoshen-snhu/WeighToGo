import { ThemeProvider } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { theme } from '../../../theme/theme';
import { RegisterForm } from './RegisterForm';

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

const valid = {
  displayName: 'Jane Doe',
  email: 'jane@example.com',
  password: 'Aa1!aaaaaaaa',
  confirmPassword: 'Aa1!aaaaaaaa',
};

describe('RegisterForm', () => {
  it('renders all required fields and a submit button', () => {
    render(
      <Wrapper>
        <RegisterForm onSubmit={vi.fn()} status="idle" />
      </Wrapper>,
    );
    expect(screen.getByLabelText(/display name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
  });

  it('shows a client-side error for invalid email', async () => {
    render(
      <Wrapper>
        <RegisterForm onSubmit={vi.fn()} status="idle" />
      </Wrapper>,
    );
    await userEvent.type(screen.getByLabelText(/email/i), 'bad-email');
    await userEvent.click(screen.getByRole('button', { name: /create account/i }));
    expect(await screen.findByText(/enter a valid email address/i)).toBeInTheDocument();
  });

  it('shows an error for password shorter than 12 chars', async () => {
    render(
      <Wrapper>
        <RegisterForm onSubmit={vi.fn()} status="idle" />
      </Wrapper>,
    );
    await userEvent.type(screen.getByLabelText(/^password$/i), 'Aa1!aaaa');
    await userEvent.click(screen.getByRole('button', { name: /create account/i }));
    expect(await screen.findByText(/at least 12 characters/i)).toBeInTheDocument();
  });

  it('shows "passwords must match" when confirmPassword differs', async () => {
    render(
      <Wrapper>
        <RegisterForm onSubmit={vi.fn()} status="idle" />
      </Wrapper>,
    );
    await userEvent.type(screen.getByLabelText(/^password$/i), 'Aa1!aaaaaaaa');
    await userEvent.type(screen.getByLabelText(/confirm password/i), 'different');
    await userEvent.click(screen.getByRole('button', { name: /create account/i }));
    expect(await screen.findByText(/passwords must match/i)).toBeInTheDocument();
  });

  it('calls onSubmit with form values when valid', async () => {
    const onSubmit = vi.fn();
    render(
      <Wrapper>
        <RegisterForm onSubmit={onSubmit} status="idle" />
      </Wrapper>,
    );
    await userEvent.type(screen.getByLabelText(/display name/i), valid.displayName);
    await userEvent.type(screen.getByLabelText(/email/i), valid.email);
    await userEvent.type(screen.getByLabelText(/^password$/i), valid.password);
    await userEvent.type(screen.getByLabelText(/confirm password/i), valid.confirmPassword);
    await userEvent.click(screen.getByRole('button', { name: /create account/i }));
    await waitFor(() => expect(onSubmit).toHaveBeenCalled());
  });

  it('renders a form-level alert for the formError prop', () => {
    render(
      <Wrapper>
        <RegisterForm onSubmit={vi.fn()} status="idle" formError="Email already taken." />
      </Wrapper>,
    );
    const alert = screen.getByRole('alert');
    expect(alert).toHaveTextContent(/email already taken/i);
  });

  it('disables the submit button while submitting', () => {
    render(
      <Wrapper>
        <RegisterForm onSubmit={vi.fn()} status="submitting" />
      </Wrapper>,
    );
    expect(screen.getByRole('button', { name: /create account/i })).toBeDisabled();
  });
});
