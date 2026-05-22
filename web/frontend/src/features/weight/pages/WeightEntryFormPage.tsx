/**
 * Weight entry form page stub.
 *
 * The full form (date picker, weight input, unit selector, notes, validation,
 * and API submission) is implemented in Phase 6.
 *
 * Requirements: SRS §3.1 FR-05.
 */

import { Box, Typography } from '@mui/material';

/**
 * Log-a-weight page rendered at /weight/new and /weight/:entryId/edit.
 */
export function WeightEntryFormPage() {
  return (
    <Box component="main">
      <Typography variant="h4" component="h1" gutterBottom>
        Log Weight
      </Typography>
      <Typography variant="body1" color="text.secondary">
        The weight entry form is implemented in Phase 6.
      </Typography>
    </Box>
  );
}
