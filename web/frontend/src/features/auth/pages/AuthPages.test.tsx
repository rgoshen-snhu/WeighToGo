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

  it('has an accessible heading', () => {
    render(
      <Wrapper>
        <LoginPage />
      </Wrapper>,
    );
    expect(screen.getByRole('heading')).toBeInTheDocument();
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

  it('has an accessible heading', () => {
    render(
      <Wrapper>
        <RegisterPage />
      </Wrapper>,
    );
    expect(screen.getByRole('heading')).toBeInTheDocument();
  });
});
