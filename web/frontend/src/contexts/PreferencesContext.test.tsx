import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, renderHook, screen } from '@testing-library/react';
import type { ReactNode } from 'react';
import { describe, expect, it, vi } from 'vitest';

import { PreferencesProvider, usePreferences } from './PreferencesContext';

vi.mock('./AuthContext', () => ({
  useAuth: () => ({ user: { user_id: 1 }, isAuthenticated: true, isLoading: false }),
}));

vi.mock('../features/settings/api/preferences-client', () => ({
  preferencesClient: {
    fetch: vi.fn().mockResolvedValue({
      weight_unit: 'lbs',
      notify_achievement: true,
      notify_milestone: true,
      notify_streak: true,
    }),
    update: vi.fn(),
  },
}));

function wrapper({ children }: { children: ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (
    <QueryClientProvider client={qc}>
      <PreferencesProvider>{children}</PreferencesProvider>
    </QueryClientProvider>
  );
}

describe('usePreferences', () => {
  it('throws when used outside PreferencesProvider', () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => undefined);
    expect(() => renderHook(() => usePreferences())).toThrow(/PreferencesProvider/);
    spy.mockRestore();
  });

  it('defaults weightUnit to lbs while loading', () => {
    const { result } = renderHook(() => usePreferences(), { wrapper });
    expect(result.current.preferences.weightUnit).toBe('lbs');
  });

  it('exposes notifyAchievement default true', () => {
    const { result } = renderHook(() => usePreferences(), { wrapper });
    expect(result.current.preferences.notifyAchievement).toBe(true);
  });

  it('exposes notifyMilestone default true', () => {
    const { result } = renderHook(() => usePreferences(), { wrapper });
    expect(result.current.preferences.notifyMilestone).toBe(true);
  });

  it('exposes notifyStreak default true', () => {
    const { result } = renderHook(() => usePreferences(), { wrapper });
    expect(result.current.preferences.notifyStreak).toBe(true);
  });

  it('exposes isLoading boolean', () => {
    const { result } = renderHook(() => usePreferences(), { wrapper });
    expect(typeof result.current.isLoading).toBe('boolean');
  });

  it('exposes a setPreference function', () => {
    const { result } = renderHook(() => usePreferences(), { wrapper });
    expect(typeof result.current.setPreference).toBe('function');
  });

  it('does not have colorScheme on the preferences object', () => {
    const { result } = renderHook(() => usePreferences(), { wrapper });
    // colorScheme is FR-P-2, deferred. Asserting it is not present.
    expect('colorScheme' in result.current.preferences).toBe(false);
  });
});

describe('PreferencesProvider', () => {
  it('renders children', () => {
    render(
      <QueryClientProvider client={new QueryClient()}>
        <PreferencesProvider>
          <span>child node</span>
        </PreferencesProvider>
      </QueryClientProvider>,
    );
    expect(screen.getByText('child node')).toBeInTheDocument();
  });
});
