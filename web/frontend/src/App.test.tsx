import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material';

import { App } from './App';
import { AuthProvider } from './contexts/AuthContext';
import { PreferencesProvider } from './contexts/PreferencesContext';
import { theme } from './theme/theme';

/** Full provider wrapper matching the structure in main.tsx. */
function FullProviders({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <PreferencesProvider>
          <ThemeProvider theme={theme}>{children}</ThemeProvider>
        </PreferencesProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

describe('App (integration)', () => {
  it('renders without crashing with full provider setup', () => {
    render(
      <FullProviders>
        <MemoryRouter initialEntries={['/login']}>
          <App />
        </MemoryRouter>
      </FullProviders>,
    );
  });

  it('navigating to /login renders the Log In heading from LoginPage', () => {
    render(
      <FullProviders>
        <MemoryRouter initialEntries={['/login']}>
          <App />
        </MemoryRouter>
      </FullProviders>,
    );
    // LoginPage renders an h5 heading "Log In" inside AuthLayout.
    expect(screen.getByText(/log in/i)).toBeInTheDocument();
  });

  it('navigating to /register renders the Create Account heading', () => {
    render(
      <FullProviders>
        <MemoryRouter initialEntries={['/register']}>
          <App />
        </MemoryRouter>
      </FullProviders>,
    );
    expect(screen.getByText(/create account/i)).toBeInTheDocument();
  });

  it('navigating to /goals when unauthenticated redirects to /login', () => {
    render(
      <FullProviders>
        <MemoryRouter initialEntries={['/goals']}>
          <App />
        </MemoryRouter>
      </FullProviders>,
    );
    // Unauthenticated — App should redirect to login. The login page or its
    // AuthLayout branding must be visible.
    expect(screen.getByText(/weigh to go/i)).toBeInTheDocument();
    // The goals page content should NOT be visible.
    expect(screen.queryByText(/coming in milestone 3/i)).not.toBeInTheDocument();
  });
});
