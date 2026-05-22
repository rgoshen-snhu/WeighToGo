import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { ThemeProvider } from '@mui/material';
import { theme } from '../theme/theme';
import { EmptyState } from './EmptyState';

function Wrapper({ children }: { children: React.ReactNode }) {
  return <ThemeProvider theme={theme}>{children}</ThemeProvider>;
}

describe('EmptyState', () => {
  it('renders without crashing', () => {
    render(
      <Wrapper>
        <EmptyState title="Nothing here" description="No data yet." />
      </Wrapper>,
    );
  });

  it('renders the title', () => {
    render(
      <Wrapper>
        <EmptyState title="Nothing here" description="No data yet." />
      </Wrapper>,
    );
    expect(screen.getByText('Nothing here')).toBeInTheDocument();
  });

  it('renders the description', () => {
    render(
      <Wrapper>
        <EmptyState title="Nothing here" description="No data yet." />
      </Wrapper>,
    );
    expect(screen.getByText('No data yet.')).toBeInTheDocument();
  });

  it('renders an optional action when provided', () => {
    render(
      <Wrapper>
        <EmptyState
          title="Nothing here"
          description="No data."
          action={<button type="button">Add item</button>}
        />
      </Wrapper>,
    );
    expect(
      screen.getByRole('button', { name: /add item/i }),
    ).toBeInTheDocument();
  });
});
