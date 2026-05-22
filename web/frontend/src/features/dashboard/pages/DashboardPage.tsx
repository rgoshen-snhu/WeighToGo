/**
 * Dashboard page stub.
 *
 * The full dashboard (recent weight trend chart, last entry summary, quick-log
 * shortcut) is implemented in Phase 6 and Phase 7.
 *
 * Requirements: SRS §3.1 FR-04, FR-05.
 */

import { Box, Typography } from '@mui/material';

/**
 * Dashboard landing page rendered at /.
 */
export function DashboardPage() {
  return (
    <Box component="main">
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Your weight summary will appear here once Phase 6 is complete.
      </Typography>
    </Box>
  );
}
