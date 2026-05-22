/**
 * Application entry point.
 *
 * Mounts the provider tree in the following order (outermost → innermost):
 *
 * 1. StrictMode     — React double-invoke checks in development
 * 2. BrowserRouter  — React Router context
 * 3. QueryClientProvider — TanStack Query server-state cache
 * 4. AuthProvider   — authentication state (user, isAuthenticated)
 * 5. PreferencesProvider — display preferences (unit, colour scheme)
 * 6. ThemeProvider  — Material UI theme
 * 7. CssBaseline    — normalize browser stylesheets
 *
 * The split between main.tsx (BrowserRouter) and App.tsx (Routes) allows
 * tests to supply a MemoryRouter without altering the component tree.
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { CssBaseline, ThemeProvider } from '@mui/material';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';

import { App } from './App';
import { AuthProvider } from './contexts/AuthContext';
import { PreferencesProvider } from './contexts/PreferencesContext';
import { theme } from './theme/theme';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Disable automatic retries in the scaffold — Phase 6 will tune these.
      retry: false,
      staleTime: 60_000,
    },
  },
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <PreferencesProvider>
            <ThemeProvider theme={theme}>
              <CssBaseline />
              <App />
            </ThemeProvider>
          </PreferencesProvider>
        </AuthProvider>
      </QueryClientProvider>
    </BrowserRouter>
  </StrictMode>,
);
