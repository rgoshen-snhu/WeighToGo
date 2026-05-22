/**
 * Navigation item list for the app drawer.
 *
 * Receives a typed array of RouteConfig entries and renders a MUI List of
 * ListItemButton links for every entry where showInNav is true. No hardcoded
 * branch logic lives here — the caller controls which routes are passed.
 *
 * SRS §10.2 specifies the NavList behaviour.
 */

import { List, ListItemButton, ListItemText } from '@mui/material';
import { Link } from 'react-router-dom';
import type { RouteConfig } from '../routes';

interface NavListProps {
  /** Route entries to render. Only showInNav === true items are displayed. */
  items: RouteConfig[];
}

/**
 * Renders navigable list items from the provided route configuration.
 */
export function NavList({ items }: NavListProps) {
  const visibleItems = items.filter((item) => item.showInNav === true);

  return (
    <List component="nav" aria-label="main navigation">
      {visibleItems.map((item) => (
        <ListItemButton key={item.path} component={Link} to={item.path}>
          <ListItemText primary={item.label} />
        </ListItemButton>
      ))}
    </List>
  );
}
