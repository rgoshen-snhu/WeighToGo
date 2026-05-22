import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { ThemeProvider } from '@mui/material';
import { theme } from '../../../theme/theme';

import { DashboardPage } from './DashboardPage';

function Wrapper({ children }: { children: React.ReactNode }) {
  return (
    <MemoryRouter>
      <ThemeProvider theme={theme}>{children}</ThemeProvider>
    </MemoryRouter>
  );
}

describe('DashboardPage', () => {
  it('renders without crashing', () => {
    render(
      <Wrapper>
        <DashboardPage />
      </Wrapper>,
    );
  });

  it('has an accessible heading', () => {
    render(
      <Wrapper>
        <DashboardPage />
      </Wrapper>,
    );
    expect(screen.getByRole('heading')).toBeInTheDocument();
  });
});
