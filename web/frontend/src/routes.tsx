/**
 * Declarative route configuration for the Weigh to Go! web application.
 *
 * Separating route declarations from the component tree keeps the routing
 * contract explicit and testable without mounting a full component hierarchy.
 *
 * SRS §10.1 governs the route structure.
 */

/**
 * A single route entry used by both the router and the navigation list.
 */
export interface RouteConfig {
  /** URL path for the route (e.g. '/weight'). */
  path: string;
  /** Human-readable label shown in navigation and page titles. */
  label: string;
  /** Whether the route should appear in the side navigation drawer. */
  showInNav?: boolean;
  /**
   * Icon name from @mui/icons-material. Used by NavList to resolve the icon
   * component. Kept as a string here so this module stays free of MUI imports.
   */
  iconName?: string;
}

/**
 * Routes accessible without authentication.
 *
 * Visiting any of these routes while already authenticated should redirect to
 * the dashboard. The redirect logic lives in the router, not here.
 */
export const publicRoutes: RouteConfig[] = [
  { path: '/login', label: 'Login' },
  { path: '/register', label: 'Create Account' },
];

/**
 * Routes that require an authenticated session.
 *
 * Unauthenticated access to any protected route redirects to
 * `/login?from=<original-path>`.  The ProtectedRoute wrapper in App.tsx
 * implements that redirect — these declarations are pure data.
 */
export const protectedRoutes: RouteConfig[] = [
  { path: '/', label: 'Dashboard', showInNav: true, iconName: 'Dashboard' },
  {
    path: '/weight',
    label: 'Weight Log',
    showInNav: true,
    iconName: 'FitnessCenter',
  },
  {
    path: '/weight/new',
    label: 'Log Weight',
    showInNav: false,
    iconName: 'Add',
  },
  { path: '/goals', label: 'Goals', showInNav: true, iconName: 'Flag' },
  {
    path: '/achievements',
    label: 'Achievements',
    showInNav: true,
    iconName: 'EmojiEvents',
  },
  {
    path: '/settings',
    label: 'Settings',
    showInNav: true,
    iconName: 'Settings',
  },
];
