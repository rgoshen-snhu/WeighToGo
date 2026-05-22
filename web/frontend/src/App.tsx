/**
 * Root application component.
 *
 * Declares the route hierarchy and the ProtectedRoute wrapper that redirects
 * unauthenticated users to /login. The component itself does not own a
 * BrowserRouter — that is provided by main.tsx so tests can supply a
 * MemoryRouter instead.
 *
 * SRS §10.1 governs the route structure.
 */

import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import type { ReactNode } from 'react';

import { AppLayout } from './components/AppLayout';
import { useAuth } from './contexts/AuthContext';
import { DashboardPage } from './features/dashboard/pages/DashboardPage';
import { LoginPage } from './features/auth/pages/LoginPage';
import { RegisterPage } from './features/auth/pages/RegisterPage';
import { AchievementsPlaceholderPage } from './features/placeholders/AchievementsPlaceholderPage';
import { GoalsPlaceholderPage } from './features/placeholders/GoalsPlaceholderPage';
import { SettingsPlaceholderPage } from './features/placeholders/SettingsPlaceholderPage';
import { WeightHistoryPage } from './features/weight/pages/WeightHistoryPage';
import { WeightEntryFormPage } from './features/weight/pages/WeightEntryFormPage';

/**
 * Wraps a route element so that unauthenticated users are redirected to
 * /login?from=<original-path> before the protected page renders.
 */
function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    const params = new URLSearchParams({ from: location.pathname });
    return <Navigate to={`/login?${params.toString()}`} replace />;
  }

  return <>{children}</>;
}

/**
 * Declares the full route hierarchy.
 *
 * Public routes (login, register) use AuthLayout via the page components
 * themselves. Protected routes are nested inside AppLayout via a wrapping
 * Route + ProtectedRoute.
 */
export function App() {
  return (
    <Routes>
      {/* ── Public routes (no navigation) ─────────────────────────── */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* ── Protected routes (inside AppLayout) ───────────────────── */}
      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="/weight" element={<WeightHistoryPage />} />
        <Route path="/weight/new" element={<WeightEntryFormPage />} />
        <Route path="/weight/:entryId/edit" element={<WeightEntryFormPage />} />
        <Route path="/goals" element={<GoalsPlaceholderPage />} />
        <Route path="/achievements" element={<AchievementsPlaceholderPage />} />
        <Route path="/settings" element={<SettingsPlaceholderPage />} />
      </Route>

      {/* ── Fallback ─────────────────────────────────────────────── */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
