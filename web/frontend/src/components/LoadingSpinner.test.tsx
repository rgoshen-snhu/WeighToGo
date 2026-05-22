import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { ThemeProvider } from '@mui/material';
import { theme } from '../theme/theme';
import { LoadingSpinner } from './LoadingSpinner';

function Wrapper({ children }: { children: React.ReactNode }) {
  return <ThemeProvider theme={theme}>{children}</ThemeProvider>;
}

describe('LoadingSpinner', () => {
  it('renders without crashing', () => {
    render(
      <Wrapper>
        <LoadingSpinner />
      </Wrapper>,
    );
  });

  it('has an accessible label', () => {
    render(
      <Wrapper>
        <LoadingSpinner />
      </Wrapper>,
    );
    // The spinner should have an accessible role or aria-label so screen
    // readers can announce it.
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('accepts a custom aria-label', () => {
    render(
      <Wrapper>
        <LoadingSpinner label="Loading your data" />
      </Wrapper>,
    );
    expect(
      screen.getByRole('progressbar', { name: /loading your data/i }),
    ).toBeInTheDocument();
  });
});
