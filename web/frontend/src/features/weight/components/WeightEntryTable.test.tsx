import { ThemeProvider } from '@mui/material/styles';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';

import type { WeightEntryRecord } from '../api/weight-client';
import { theme } from '../../../theme/theme';
import { WeightEntryTable } from './WeightEntryTable';

const entries: WeightEntryRecord[] = [
  {
    entry_id: 1,
    weight_value: 175.5,
    weight_unit: 'lbs',
    observation_date: '2026-05-20',
    notes: null,
    created_at: '2026-05-20T12:00:00Z',
    updated_at: '2026-05-20T12:00:00Z',
  },
  {
    entry_id: 2,
    weight_value: 174.0,
    weight_unit: 'lbs',
    observation_date: '2026-05-19',
    notes: 'Morning',
    created_at: '2026-05-19T08:00:00Z',
    updated_at: '2026-05-19T08:00:00Z',
  },
];

function renderTable(props: Partial<Parameters<typeof WeightEntryTable>[0]> = {}) {
  const defaults = {
    entries,
    onDelete: vi.fn(),
  };
  return render(
    <ThemeProvider theme={theme}>
      <MemoryRouter>
        <WeightEntryTable {...defaults} {...props} />
      </MemoryRouter>
    </ThemeProvider>,
  );
}

describe('WeightEntryTable', () => {
  it('renders the correct number of rows', () => {
    renderTable();
    // Each entry has an edit and a delete button; look for delete buttons
    expect(screen.getAllByRole('button', { name: /delete/i })).toHaveLength(2);
  });

  it('displays weight values', () => {
    renderTable();
    expect(screen.getByText(/175/)).toBeInTheDocument();
    expect(screen.getByText(/174/)).toBeInTheDocument();
  });

  it('calls onDelete when Delete button is clicked', async () => {
    const onDelete = vi.fn();
    renderTable({ onDelete });
    const [firstDelete] = screen.getAllByRole('button', { name: /delete/i });
    await userEvent.click(firstDelete!);
    expect(onDelete).toHaveBeenCalledWith(1);
  });

  it('renders Edit links', () => {
    renderTable();
    const editLinks = screen.getAllByRole('link', { name: /edit/i });
    expect(editLinks.length).toBeGreaterThan(0);
  });

  it('renders empty message when entries is empty', () => {
    renderTable({ entries: [] });
    expect(screen.getByText(/no entries/i)).toBeInTheDocument();
  });

  // F5 / SRS NFR-A-5: interactive targets must be at least 44 × 44 CSS pixels
  // (both height and width). The floor is enforced at the theme level via
  // MuiButton and MuiIconButton styleOverrides (see web/frontend/src/theme/
  // theme.ts) so all controls inherit it. MUI compiles styleOverrides to an
  // emotion-generated CSS class injected into the document <head> — not to
  // an inline style attribute — so the floor only applies when the component
  // tree is wrapped in ThemeProvider (asserted here via renderTable). The
  // toHaveStyle matcher resolves the value via window.getComputedStyle, which
  // reads from the injected stylesheet rather than the element's inline style.
  it('renders Edit action meeting the 44px target floor (height and width)', () => {
    renderTable();
    const editLink = screen.getAllByRole('link', { name: /edit entry from/i })[0];
    expect(editLink).toBeDefined();
    expect(editLink).toHaveStyle({ minHeight: '44px', minWidth: '44px' });
  });

  it('renders Delete action meeting the 44px target floor (height and width)', () => {
    renderTable();
    const deleteButton = screen.getAllByRole('button', { name: /delete entry from/i })[0];
    expect(deleteButton).toBeDefined();
    expect(deleteButton).toHaveStyle({ minHeight: '44px', minWidth: '44px' });
  });
});
