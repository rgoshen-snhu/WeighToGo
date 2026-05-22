import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { ThemeProvider } from '@mui/material';
import { theme } from '../../../theme/theme';

import { LoginPage } from './LoginPage';
import { RegisterPage } from './RegisterPage';

function Wrapper({ children }: { children: React.ReactNode }) {
  return (
    <MemoryRouter>
      <ThemeProvider theme={theme}>{children}</ThemeProvider>
    </MemoryRouter>
  );
}

describe('LoginPage', () => {
  it('renders without crashing', () => {
    render(
      <Wrapper>
        <LoginPage />
      </Wrapper>,
    );
  });

  it('has at least one accessible heading', () => {
    render(
      <Wrapper>
        <LoginPage />
      </Wrapper>,
    );
    // AuthLayout adds an h1 branding heading; the page adds its own h5.
    expect(screen.getAllByRole('heading').length).toBeGreaterThan(0);
  });
});

describe('RegisterPage', () => {
  it('renders without crashing', () => {
    render(
      <Wrapper>
        <RegisterPage />
      </Wrapper>,
    );
  });

  it('has at least one accessible heading', () => {
    render(
      <Wrapper>
        <RegisterPage />
      </Wrapper>,
    );
    expect(screen.getAllByRole('heading').length).toBeGreaterThan(0);
  });
});
