import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { ThemeProvider } from '@mui/material';
import { theme } from '../theme/theme';
import { AuthProvider } from '../contexts/AuthContext';
import { AppLayout } from './AppLayout';

function Wrapper({ children }: { children: React.ReactNode }) {
  return (
    <MemoryRouter>
      <ThemeProvider theme={theme}>
        <AuthProvider>{children}</AuthProvider>
      </ThemeProvider>
    </MemoryRouter>
  );
}

describe('AppLayout', () => {
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
});
