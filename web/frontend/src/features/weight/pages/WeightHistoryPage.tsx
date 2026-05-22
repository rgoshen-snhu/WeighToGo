/**
 * Weight history page stub.
 *
 * The full history view (sortable / filterable table, pagination, delete)
 * is implemented in Phase 6.
 *
 * Requirements: SRS §3.1 FR-06.
 */

import { Box, Typography } from '@mui/material';

/**
 * Weight log history page rendered at /weight.
 */
export function WeightHistoryPage() {
  return (
    <Box component="main">
      <Typography variant="h4" component="h1" gutterBottom>
        Weight Log
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Your weight history will appear here once Phase 6 is complete.
      </Typography>
    </Box>
  );
}
