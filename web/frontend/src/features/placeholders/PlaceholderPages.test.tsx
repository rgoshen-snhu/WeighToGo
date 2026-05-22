import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { ThemeProvider } from '@mui/material';
import { theme } from '../../theme/theme';

import { GoalsPlaceholderPage } from './GoalsPlaceholderPage';
import { AchievementsPlaceholderPage } from './AchievementsPlaceholderPage';
import { SettingsPlaceholderPage } from './SettingsPlaceholderPage';

function Wrapper({ children }: { children: React.ReactNode }) {
  return <ThemeProvider theme={theme}>{children}</ThemeProvider>;
}

describe('GoalsPlaceholderPage', () => {
  it('renders without crashing', () => {
    render(
      <Wrapper>
        <GoalsPlaceholderPage />
      </Wrapper>,
    );
  });

  it('has an accessible heading', () => {
    render(
      <Wrapper>
        <GoalsPlaceholderPage />
      </Wrapper>,
    );
    expect(screen.getByRole('heading')).toBeInTheDocument();
  });

  it('contains "Coming in Milestone 3" notice', () => {
    render(
      <Wrapper>
        <GoalsPlaceholderPage />
      </Wrapper>,
    );
    expect(screen.getByText(/coming in milestone 3/i)).toBeInTheDocument();
  });
});

describe('AchievementsPlaceholderPage', () => {
  it('renders without crashing', () => {
    render(
      <Wrapper>
        <AchievementsPlaceholderPage />
      </Wrapper>,
    );
  });

  it('has an accessible heading', () => {
    render(
      <Wrapper>
        <AchievementsPlaceholderPage />
      </Wrapper>,
    );
    expect(screen.getByRole('heading')).toBeInTheDocument();
  });

  it('contains "Coming in Milestone 3" notice', () => {
    render(
      <Wrapper>
        <AchievementsPlaceholderPage />
      </Wrapper>,
    );
    expect(screen.getByText(/coming in milestone 3/i)).toBeInTheDocument();
  });
});

describe('SettingsPlaceholderPage', () => {
  it('renders without crashing', () => {
    render(
      <Wrapper>
        <SettingsPlaceholderPage />
      </Wrapper>,
    );
  });

  it('has an accessible heading', () => {
    render(
      <Wrapper>
        <SettingsPlaceholderPage />
      </Wrapper>,
    );
    expect(screen.getByRole('heading')).toBeInTheDocument();
  });

  it('contains "Coming in Milestone 3" notice', () => {
    render(
      <Wrapper>
        <SettingsPlaceholderPage />
      </Wrapper>,
    );
    expect(screen.getByText(/coming in milestone 3/i)).toBeInTheDocument();
  });
});
