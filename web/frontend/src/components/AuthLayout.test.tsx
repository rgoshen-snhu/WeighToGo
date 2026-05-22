import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { ThemeProvider } from '@mui/material';
import { theme } from '../theme/theme';
import { AuthLayout } from './AuthLayout';

function Wrapper({ children }: { children: React.ReactNode }) {
  return <ThemeProvider theme={theme}>{children}</ThemeProvider>;
}

describe('AuthLayout', () => {
  it('renders without crashing', () => {
    render(
      <Wrapper>
        <AuthLayout>
          <span>content</span>
        </AuthLayout>
      </Wrapper>,
    );
  });

  it('renders its children', () => {
    render(
      <Wrapper>
        <AuthLayout>
          <span>auth child</span>
        </AuthLayout>
      </Wrapper>,
    );
    expect(screen.getByText('auth child')).toBeInTheDocument();
  });

  it('renders the application name branding', () => {
    render(
      <Wrapper>
        <AuthLayout>
          <span>child</span>
        </AuthLayout>
      </Wrapper>,
    );
    expect(
      screen.getByText(/weigh to go/i),
    ).toBeInTheDocument();
  });
});
