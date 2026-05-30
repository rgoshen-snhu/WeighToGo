import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import type { RateOfChangeResponse } from '../api/dashboard-client';
import { RateOfChangeCard } from './RateOfChangeCard';

const prefs = { current: 'lbs' as 'lbs' | 'kg' };
vi.mock('../../../contexts/PreferencesContext', () => ({
  usePreferences: () => ({
    preferences: {
      weightUnit: prefs.current,
      notifyAchievement: true,
      notifyMilestone: true,
      notifyStreak: true,
    },
    isLoading: false,
    setPreference: () => {},
  }),
}));

beforeEach(() => {
  prefs.current = 'lbs';
});

const falling: RateOfChangeResponse = {
  weekly_rate: -0.8,
  unit: 'lbs',
  reason: null,
};

const rising: RateOfChangeResponse = {
  weekly_rate: 1.2,
  unit: 'lbs',
  reason: null,
};

const insufficient: RateOfChangeResponse = {
  weekly_rate: null,
  unit: null,
  reason: 'insufficient_data',
};

describe('RateOfChangeCard', () => {
  it('renders the Rate of Change title', () => {
    render(<RateOfChangeCard rateOfChange={insufficient} isLoading={false} isError={false} />);
    expect(screen.getByText(/rate of change/i)).toBeInTheDocument();
  });

  it('renders a falling rate with unit and downward wording', () => {
    render(<RateOfChangeCard rateOfChange={falling} isLoading={false} isError={false} />);
    expect(screen.getByText(/down/i)).toBeInTheDocument();
    expect(screen.getByText(/0\.8/)).toBeInTheDocument();
    expect(screen.getByText(/lbs\s*\/\s*week/i)).toBeInTheDocument();
  });

  it('renders a rising rate with upward wording', () => {
    render(<RateOfChangeCard rateOfChange={rising} isLoading={false} isError={false} />);
    expect(screen.getByText(/up/i)).toBeInTheDocument();
    expect(screen.getByText(/1\.2/)).toBeInTheDocument();
  });

  it('converts the rate magnitude to the preferred unit (kg)', () => {
    prefs.current = 'kg';
    // backend rate is -2 lbs/week -> 0.9 kg/week
    const fallingLbs: RateOfChangeResponse = { weekly_rate: -2, unit: 'lbs', reason: null };
    render(<RateOfChangeCard rateOfChange={fallingLbs} isLoading={false} isError={false} />);
    expect(screen.getByText(/down/i)).toBeInTheDocument();
    expect(screen.getByText(/0\.9/)).toBeInTheDocument();
    expect(screen.getByText(/kg\s*\/\s*week/i)).toBeInTheDocument();
  });

  it('does not convert when the backend unit is null (falls back gracefully)', () => {
    prefs.current = 'kg';
    // Non-null rate with null unit is type-possible; treat the magnitude as-is.
    const nullUnit: RateOfChangeResponse = { weekly_rate: -2, unit: null, reason: null };
    render(<RateOfChangeCard rateOfChange={nullUnit} isLoading={false} isError={false} />);
    // 2.0 unconverted, no unit suffix. Match against the raw textContent with
    // whitespace normalisation disabled so a dangling space where the unit
    // would have gone (the double-space regression) fails the assertion.
    const node = screen.getByText('Down 2.0 / week', {
      normalizer: (text) => text,
    });
    expect(node).toBeInTheDocument();
  });

  it('renders a no-change message when the rate is zero', () => {
    const flat: RateOfChangeResponse = { weekly_rate: 0, unit: 'lbs', reason: null };
    render(<RateOfChangeCard rateOfChange={flat} isLoading={false} isError={false} />);
    expect(screen.getByText(/no change/i)).toBeInTheDocument();
  });

  it('renders no-change when a small rate rounds to 0.0 at one decimal', () => {
    const negligible: RateOfChangeResponse = { weekly_rate: -0.04, unit: 'lbs', reason: null };
    render(<RateOfChangeCard rateOfChange={negligible} isLoading={false} isError={false} />);
    expect(screen.getByText(/no change/i)).toBeInTheDocument();
    expect(screen.queryByText(/down/i)).not.toBeInTheDocument();
  });

  it('renders a not-enough-data message when the rate is null', () => {
    render(<RateOfChangeCard rateOfChange={insufficient} isLoading={false} isError={false} />);
    expect(screen.getByText(/not enough data/i)).toBeInTheDocument();
  });

  it('shows loading text while loading', () => {
    render(<RateOfChangeCard rateOfChange={undefined} isLoading={true} isError={false} />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('shows an error message on error', () => {
    render(<RateOfChangeCard rateOfChange={undefined} isLoading={false} isError={true} />);
    expect(screen.getByText(/failed to load/i)).toBeInTheDocument();
  });
});
