/**
 * Achievements placeholder page — displayed while the Achievements feature is
 * pending implementation in Milestone 3.
 *
 * Requirements: SRS §3.1 FR-11 through FR-12 (achievements and badges).
 */

import { Box, Paper, Typography } from '@mui/material';

/**
 * Accessible placeholder that informs users when the Achievements feature will
 * be available and what it will offer.
 */
export function AchievementsPlaceholderPage() {
  return (
    <Box component="main" sx={{ maxWidth: 600, mx: 'auto', py: 4 }}>
      <Paper elevation={0} sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Achievements
        </Typography>
        <Typography variant="subtitle1" component="p" color="primary" gutterBottom>
          Coming in Milestone 3
        </Typography>
        <Typography variant="body1" color="text.secondary">
          The Achievements feature will award badges and recognition when you reach important
          milestones on your weight-management journey.
        </Typography>
      </Paper>
    </Box>
  );
}
