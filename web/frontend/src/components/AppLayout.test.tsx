import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material';
import { theme } from '../theme/theme';
import { AuthProvider } from '../contexts/AuthContext';
import { authClient, type AuthUser } from '../features/auth/api/auth-client';
import { AppLayout } from './AppLayout';

function Wrapper({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <ThemeProvider theme={theme}>
          <AuthProvider>{children}</AuthProvider>
        </ThemeProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe('AppLayout', () => {
  beforeEach(() => {
    vi.spyOn(authClient, 'me').mockRejectedValue(new Error('401'));
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders without crashing', () => {
    render(
      <Wrapper>
        <AppLayout />
      </Wrapper>,
    );
  });

  it('renders the application name in the app bar', () => {
    render(
      <Wrapper>
        <AppLayout />
      </Wrapper>,
    );
    expect(screen.getByText(/weigh to go/i)).toBeInTheDocument();
  });

  it('renders navigation landmark', () => {
    render(
      <Wrapper>
        <AppLayout />
      </Wrapper>,
    );
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });

  it('renders UserMenu avatar when user is authenticated', async () => {
    const authenticatedUser: AuthUser = {
      user_id: 1,
      email: 'user@example.com',
      display_name: 'Test User',
      created_at: '2026-05-23T00:00:00Z',
    };
    vi.spyOn(authClient, 'me').mockResolvedValue(authenticatedUser);
    render(
      <Wrapper>
        <AppLayout />
      </Wrapper>,
    );
    await waitFor(() =>
      expect(
        screen.getByRole('button', { name: /account menu for test user/i }),
      ).toBeInTheDocument(),
    );
  });
});
