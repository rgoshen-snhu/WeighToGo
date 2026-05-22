import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { ThemeProvider } from '@mui/material';
import { theme } from '../../../theme/theme';

import { WeightHistoryPage } from './WeightHistoryPage';
import { WeightEntryFormPage } from './WeightEntryFormPage';

function Wrapper({ children }: { children: React.ReactNode }) {
  return (
    <MemoryRouter>
      <ThemeProvider theme={theme}>{children}</ThemeProvider>
    </MemoryRouter>
  );
}

describe('WeightHistoryPage', () => {
  it('renders without crashing', () => {
    render(
      <Wrapper>
        <WeightHistoryPage />
      </Wrapper>,
    );
  });

  it('has an accessible heading', () => {
    render(
      <Wrapper>
        <WeightHistoryPage />
      </Wrapper>,
    );
    expect(screen.getByRole('heading')).toBeInTheDocument();
  });
});

describe('WeightEntryFormPage', () => {
  it('renders without crashing', () => {
    render(
      <Wrapper>
        <WeightEntryFormPage />
      </Wrapper>,
    );
  });

  it('has an accessible heading', () => {
    render(
      <Wrapper>
        <WeightEntryFormPage />
      </Wrapper>,
    );
    expect(screen.getByRole('heading')).toBeInTheDocument();
  });
});
