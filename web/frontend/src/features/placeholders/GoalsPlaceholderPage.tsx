/**
 * Goals placeholder page — displayed while the Goals feature is pending
 * implementation in Milestone 3.
 *
 * Requirements: SRS §3.1 FR-07 through FR-10 (goal management).
 */

import { Box, Paper, Typography } from '@mui/material';

/**
 * Accessible placeholder that informs users when the Goals feature will be
 * available and what it will allow them to do.
 */
export function GoalsPlaceholderPage() {
  return (
    <Box component="main" sx={{ maxWidth: 600, mx: 'auto', py: 4 }}>
      <Paper elevation={0} sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Goals
        </Typography>
        <Typography variant="subtitle1" component="p" color="primary" gutterBottom>
          Coming in Milestone 3
        </Typography>
        <Typography variant="body1" color="text.secondary">
          The Goals feature will let you set a target weight and track your progress over time with
          visual charts and milestone celebrations.
        </Typography>
      </Paper>
    </Box>
  );
}
