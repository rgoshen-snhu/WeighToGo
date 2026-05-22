/**
 * Reusable loading indicator.
 *
 * Centres a MUI CircularProgress with a default accessible label. Pages that
 * need a context-specific announcement can supply the optional `label` prop.
 */

import { Box, CircularProgress } from '@mui/material';

interface LoadingSpinnerProps {
  /** Accessible label announced by screen readers. Defaults to "Loading". */
  label?: string;
}

/**
 * Vertically and horizontally centred circular progress indicator.
 */
export function LoadingSpinner({ label = 'Loading' }: LoadingSpinnerProps) {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        py: 8,
      }}
    >
      <CircularProgress aria-label={label} />
    </Box>
  );
}
