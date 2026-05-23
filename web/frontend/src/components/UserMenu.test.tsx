import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { authClient, type AuthUser } from '../features/auth/api/auth-client';
import { AuthProvider } from '../contexts/AuthContext';
import { UserMenu } from './UserMenu';

const user: AuthUser = {
  user_id: 1,
  email: 'jane@example.com',
  display_name: 'Jane Doe',
  created_at: '2026-05-23T00:00:00Z',
};

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <AuthProvider>{children}</AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe('UserMenu', () => {
  beforeEach(() => {
    vi.spyOn(authClient, 'me').mockResolvedValue(user);
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders an avatar button labeled with the user display name', async () => {
    render(<UserMenu />, { wrapper });
    await waitFor(() =>
      expect(
        screen.getByRole('button', { name: /account menu for jane doe/i }),
      ).toBeInTheDocument(),
    );
  });

  it('opens a menu showing email and Log out on click', async () => {
    render(<UserMenu />, { wrapper });
    await waitFor(() => screen.getByRole('button', { name: /account menu/i }));
    await userEvent.click(screen.getByRole('button', { name: /account menu/i }));
    expect(screen.getByText('jane@example.com')).toBeInTheDocument();
    expect(screen.getByRole('menuitem', { name: /log out/i })).toBeInTheDocument();
  });

  it('closes the menu on Escape', async () => {
    render(<UserMenu />, { wrapper });
    await waitFor(() => screen.getByRole('button', { name: /account menu/i }));
    await userEvent.click(screen.getByRole('button', { name: /account menu/i }));
    await userEvent.keyboard('{Escape}');
    await waitFor(() =>
      expect(screen.queryByRole('menuitem', { name: /log out/i })).not.toBeInTheDocument(),
    );
  });
});
