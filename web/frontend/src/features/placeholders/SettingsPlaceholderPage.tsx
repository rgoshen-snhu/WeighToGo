/**
 * Settings placeholder page — displayed while the Settings feature is pending
 * implementation in Milestone 3.
 *
 * Requirements: SRS §3.1 FR-13 through FR-15 (user preferences).
 */

import { Box, Paper, Typography } from '@mui/material';

/**
 * Accessible placeholder that informs users when Settings will be available
 * and what options it will expose.
 */
export function SettingsPlaceholderPage() {
  return (
    <Box component="main" sx={{ maxWidth: 600, mx: 'auto', py: 4 }}>
      <Paper elevation={0} sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Settings
        </Typography>
        <Typography variant="subtitle1" component="p" color="primary" gutterBottom>
          Coming in Milestone 3
        </Typography>
        <Typography variant="body1" color="text.secondary">
          The Settings page will let you update your profile, choose your preferred weight unit (lbs
          or kg), and personalise the application appearance.
        </Typography>
      </Paper>
    </Box>
  );
}
