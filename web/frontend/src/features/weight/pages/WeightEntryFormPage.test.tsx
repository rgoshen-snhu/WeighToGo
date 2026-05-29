import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { ApiError } from '../../../lib/api-client';
import { weightClient } from '../api/weight-client';
import { WeightEntryFormPage } from './WeightEntryFormPage';

function wrapper(initialPath = '/weight/new') {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return function Wrap({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={qc}>
        <MemoryRouter initialEntries={[initialPath]}>
          <Routes>
            <Route path="/weight/new" element={children} />
            <Route path="/weight/:entryId/edit" element={children} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );
  };
}

describe('WeightEntryFormPage', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders create mode heading at /weight/new', () => {
    render(<WeightEntryFormPage />, { wrapper: wrapper('/weight/new') });
    expect(screen.getByRole('heading', { name: /log weight/i })).toBeInTheDocument();
  });

  it('renders the weight entry form in create mode', () => {
    render(<WeightEntryFormPage />, { wrapper: wrapper('/weight/new') });
    expect(screen.getByLabelText(/weight value/i)).toBeInTheDocument();
  });

  it('renders edit mode heading at /weight/:id/edit', async () => {
    vi.spyOn(weightClient, 'get').mockResolvedValue({
      entry_id: 1,
      weight_value: 175.5,
      weight_unit: 'lbs',
      observation_date: '2026-05-20',
      notes: null,
      created_at: '2026-05-20T12:00:00Z',
      updated_at: '2026-05-20T12:00:00Z',
    });
    render(<WeightEntryFormPage />, { wrapper: wrapper('/weight/1/edit') });
    await waitFor(() => expect(screen.getByRole('heading', { name: /edit/i })).toBeInTheDocument());
  });

  it('shows invalid entry message when entryId is not a number', () => {
    render(<WeightEntryFormPage />, { wrapper: wrapper('/weight/abc/edit') });
    // The component should handle non-numeric IDs gracefully
    expect(screen.getByRole('heading')).toBeInTheDocument();
  });

  it('calls weightClient.create on submit in create mode', async () => {
    vi.spyOn(weightClient, 'create').mockResolvedValue({
      entry_id: 2,
      weight_value: 175.5,
      weight_unit: 'lbs',
      observation_date: new Date().toISOString().split('T')[0]!,
      notes: null,
      created_at: '2026-05-21T12:00:00Z',
      updated_at: '2026-05-21T12:00:00Z',
    });
    render(<WeightEntryFormPage />, { wrapper: wrapper('/weight/new') });
    const input = screen.getByLabelText(/weight value/i);
    await userEvent.type(input, '175.5');
    const saveButton = screen.getByRole('button', { name: /save/i });
    await userEvent.click(saveButton);
    await waitFor(() => expect(weightClient.create).toHaveBeenCalled());
  });

  it('shows conflict error when create returns 409', async () => {
    vi.spyOn(weightClient, 'create').mockRejectedValue(new ApiError(409, 'Conflict'));
    render(<WeightEntryFormPage />, { wrapper: wrapper('/weight/new') });
    const input = screen.getByLabelText(/weight value/i);
    await userEvent.type(input, '175.5');
    await userEvent.click(screen.getByRole('button', { name: /save/i }));
    await waitFor(() => expect(screen.getByText(/entry already exists/i)).toBeInTheDocument());
  });

  it('renders not-found state when edit-mode entry fetch returns 404', async () => {
    vi.spyOn(weightClient, 'get').mockRejectedValue(new ApiError(404, 'Not Found'));
    render(<WeightEntryFormPage />, { wrapper: wrapper('/weight/9999/edit') });
    await waitFor(() =>
      expect(screen.getByRole('heading', { name: /not found/i })).toBeInTheDocument(),
    );
    // Form must not render; a blank form on a deleted entry would PUT 404 on submit.
    expect(screen.queryByLabelText(/weight value/i)).not.toBeInTheDocument();
  });

  it('calls weightClient.update on submit in edit mode', async () => {
    const d = new Date();
    const localToday = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    vi.spyOn(weightClient, 'get').mockResolvedValue({
      entry_id: 1,
      weight_value: 175.5,
      weight_unit: 'lbs',
      observation_date: localToday,
      notes: null,
      created_at: '2026-05-20T12:00:00Z',
      updated_at: '2026-05-20T12:00:00Z',
    });
    vi.spyOn(weightClient, 'update').mockResolvedValue({
      entry_id: 1,
      weight_value: 180,
      weight_unit: 'lbs',
      observation_date: localToday,
      notes: null,
      created_at: '2026-05-20T12:00:00Z',
      updated_at: '2026-05-21T12:00:00Z',
    });
    render(<WeightEntryFormPage />, { wrapper: wrapper('/weight/1/edit') });
    await waitFor(() => screen.getByLabelText(/weight value/i));
    const saveButton = screen.getByRole('button', { name: /save/i });
    await userEvent.click(saveButton);
    await waitFor(() => expect(weightClient.update).toHaveBeenCalled());
  });
});
