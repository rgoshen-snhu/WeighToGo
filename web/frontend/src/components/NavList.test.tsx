import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { ThemeProvider } from '@mui/material';
import { theme } from '../theme/theme';
import type { RouteConfig } from '../routes';
import { NavList } from './NavList';

const navItems: RouteConfig[] = [
  { path: '/', label: 'Dashboard', showInNav: true },
  { path: '/weight', label: 'Weight Log', showInNav: true },
  { path: '/hidden', label: 'Hidden', showInNav: false },
];

function Wrapper({ children }: { children: React.ReactNode }) {
  return (
    <MemoryRouter>
      <ThemeProvider theme={theme}>{children}</ThemeProvider>
    </MemoryRouter>
  );
}

describe('NavList', () => {
  it('renders without crashing', () => {
    render(
      <Wrapper>
        <NavList items={navItems} />
      </Wrapper>,
    );
  });

  it('renders list items for showInNav routes', () => {
    render(
      <Wrapper>
        <NavList items={navItems} />
      </Wrapper>,
    );
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Weight Log')).toBeInTheDocument();
  });

  it('does not render items where showInNav is false', () => {
    render(
      <Wrapper>
        <NavList items={navItems} />
      </Wrapper>,
    );
    expect(screen.queryByText('Hidden')).not.toBeInTheDocument();
  });

  it('renders links with the correct href', () => {
    render(
      <Wrapper>
        <NavList items={navItems} />
      </Wrapper>,
    );
    const dashboardLink = screen.getByRole('link', { name: /dashboard/i });
    expect(dashboardLink).toHaveAttribute('href', '/');
  });
});
