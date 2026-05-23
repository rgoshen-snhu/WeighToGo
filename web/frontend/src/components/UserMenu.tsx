import { Avatar, Box, Divider, IconButton, Menu, MenuItem, Typography } from '@mui/material';
import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useLogout } from '../features/auth/hooks/useLogout';

/**
 * Avatar button + dropdown menu showing the current user's name, email,
 * and a log-out action.
 *
 * Renders nothing when no user is authenticated — safe to include
 * unconditionally in the AppBar.
 *
 * SRS §10.2 (AppLayout with session controls).
 */
export function UserMenu() {
  const { user } = useAuth();
  const { submit: logout, isPending } = useLogout();
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);

  if (!user) return null;

  const initials = user.display_name
    .trim()
    .split(/\s+/)
    .map((s) => s[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();

  return (
    <Box>
      <IconButton
        aria-label={`Account menu for ${user.display_name}`}
        aria-haspopup="true"
        aria-controls={anchorEl ? 'user-menu' : undefined}
        aria-expanded={!!anchorEl}
        onClick={(e) => setAnchorEl(e.currentTarget)}
      >
        <Avatar>{initials}</Avatar>
      </IconButton>
      <Menu id="user-menu" anchorEl={anchorEl} open={!!anchorEl} onClose={() => setAnchorEl(null)}>
        <Box sx={{ px: 2, py: 1 }}>
          <Typography variant="subtitle2">{user.display_name}</Typography>
          <Typography variant="body2" color="text.secondary">
            {user.email}
          </Typography>
        </Box>
        <Divider />
        <MenuItem
          onClick={() => {
            setAnchorEl(null);
            logout();
          }}
          disabled={isPending}
        >
          Log out
        </MenuItem>
      </Menu>
    </Box>
  );
}
