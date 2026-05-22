/**
 * Layout wrapper for unauthenticated screens (login, register).
 *
 * Centres a card on the viewport with the application name as branding above
 * the card. There is no navigation — auth screens are intentionally isolated.
 *
 * SRS §10.2 specifies the AuthLayout behaviour.
 */

import { Box, Container, Paper, Typography } from '@mui/material';
import type { ReactNode } from 'react';

interface AuthLayoutProps {
  children: ReactNode;
}

/**
 * Renders the centered-card auth shell around the provided children.
 */
export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <Box
      component="main"
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
        px: 2,
      }}
    >
      {/* Application branding */}
      <Typography
        variant="h4"
        component="h1"
        sx={{ mb: 3, color: 'primary.main', fontWeight: 700 }}
      >
        Weigh to Go!
      </Typography>

      {/* Centred card containing the auth form */}
      <Container maxWidth="xs">
        <Paper elevation={3} sx={{ p: 4 }}>
          {children}
        </Paper>
      </Container>
    </Box>
  );
}
