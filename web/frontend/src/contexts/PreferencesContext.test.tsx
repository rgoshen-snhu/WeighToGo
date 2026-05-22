import { act, renderHook, screen, render } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { PreferencesProvider, usePreferences } from './PreferencesContext';

describe('usePreferences', () => {
  it('throws when used outside PreferencesProvider', () => {
    const spy = vi
      .spyOn(console, 'error')
      .mockImplementation(() => undefined);
    expect(() => renderHook(() => usePreferences())).toThrow(
      /PreferencesProvider/,
    );
    spy.mockRestore();
  });

  it('defaults weightUnit to lbs', () => {
    const { result } = renderHook(() => usePreferences(), {
      wrapper: PreferencesProvider,
    });
    expect(result.current.preferences.weightUnit).toBe('lbs');
  });

  it('defaults colorScheme to light', () => {
    const { result } = renderHook(() => usePreferences(), {
      wrapper: PreferencesProvider,
    });
    expect(result.current.preferences.colorScheme).toBe('light');
  });

  it('exposes a setPreferences function', () => {
    const { result } = renderHook(() => usePreferences(), {
      wrapper: PreferencesProvider,
    });
    expect(typeof result.current.setPreferences).toBe('function');
  });

  it('setPreferences updates weightUnit', () => {
    const { result } = renderHook(() => usePreferences(), {
      wrapper: PreferencesProvider,
    });
    act(() => {
      result.current.setPreferences({ weightUnit: 'kg' });
    });
    expect(result.current.preferences.weightUnit).toBe('kg');
  });

  it('setPreferences updates colorScheme', () => {
    const { result } = renderHook(() => usePreferences(), {
      wrapper: PreferencesProvider,
    });
    act(() => {
      result.current.setPreferences({ colorScheme: 'dark' });
    });
    expect(result.current.preferences.colorScheme).toBe('dark');
  });

  it('partial setPreferences preserves unchanged fields', () => {
    const { result } = renderHook(() => usePreferences(), {
      wrapper: PreferencesProvider,
    });
    act(() => {
      result.current.setPreferences({ colorScheme: 'dark' });
    });
    // weightUnit should remain at its default.
    expect(result.current.preferences.weightUnit).toBe('lbs');
  });
});

describe('PreferencesProvider', () => {
  it('renders children', () => {
    render(
      <PreferencesProvider>
        <span>child node</span>
      </PreferencesProvider>,
    );
    expect(screen.getByText('child node')).toBeInTheDocument();
  });
});
