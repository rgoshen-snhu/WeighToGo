import { Container, Typography } from '@mui/material';

/**
 * Root application component.
 *
 * Renders the application shell. Routing, layouts, and feature pages are
 * introduced in later phases.
 */
export function App() {
  return (
    <Container component="main">
      <Typography variant="h1">Weigh to Go!</Typography>
    </Container>
  );
}
