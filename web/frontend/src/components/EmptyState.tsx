/**
 * Reusable empty-state UI component.
 *
 * Displays a centered title, description, and an optional call-to-action
 * element. Used wherever a page has no data to show yet.
 */

import { Box, Typography } from '@mui/material';
import type { ReactNode } from 'react';

interface EmptyStateProps {
  /** Short headline summarising the empty state. */
  title: string;
  /** One-sentence explanation of why the state is empty or what to do. */
  description: string;
  /** Optional action element (e.g. a Button) rendered below the description. */
  action?: ReactNode;
}

/**
 * Center-aligned empty state with title, description, and optional action.
 */
export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        py: 8,
        px: 2,
        gap: 2,
      }}
    >
      <Typography variant="h5" component="h2">
        {title}
      </Typography>
      <Typography variant="body1" color="text.secondary">
        {description}
      </Typography>
      {action}
    </Box>
  );
}
