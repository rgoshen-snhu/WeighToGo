import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { ThemeProvider } from '@mui/material';
import { theme } from '../theme/theme';
import { ErrorBoundary } from './ErrorBoundary';

function Wrapper({ children }: { children: React.ReactNode }) {
  return <ThemeProvider theme={theme}>{children}</ThemeProvider>;
}

/** Component that throws on first render. */
function ThrowingComponent() {
  throw new Error('Test render error');
}

describe('ErrorBoundary', () => {
  it('renders children when there is no error', () => {
    render(
      <Wrapper>
        <ErrorBoundary>
          <span>safe content</span>
        </ErrorBoundary>
      </Wrapper>,
    );
    expect(screen.getByText('safe content')).toBeInTheDocument();
  });

  it('renders a fallback message when a child throws', () => {
    // Suppress React's console.error for expected error output.
    const spy = vi
      .spyOn(console, 'error')
      .mockImplementation(() => undefined);

    render(
      <Wrapper>
        <ErrorBoundary>
          <ThrowingComponent />
        </ErrorBoundary>
      </Wrapper>,
    );

    expect(screen.getByRole('alert')).toBeInTheDocument();
    spy.mockRestore();
  });

  it('fallback contains a user-friendly message', () => {
    const spy = vi
      .spyOn(console, 'error')
      .mockImplementation(() => undefined);

    render(
      <Wrapper>
        <ErrorBoundary>
          <ThrowingComponent />
        </ErrorBoundary>
      </Wrapper>,
    );

    expect(
      screen.getByText(/something went wrong/i),
    ).toBeInTheDocument();
    spy.mockRestore();
  });
});
