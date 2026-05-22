/**
 * React error boundary that catches render-phase exceptions in its subtree.
 *
 * This is the one justified use of a class component in this codebase:
 * the React error boundary API requires componentDidCatch / getDerivedStateFromError,
 * which are only available on class components.
 *
 * SRS §10.2 specifies that all page slots must be wrapped in an error boundary
 * to prevent a single page's failure from crashing the entire application.
 */

import { Box, Typography } from '@mui/material';
import { Component, type ErrorInfo, type ReactNode } from 'react';

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
}

/**
 * Catches render errors anywhere in the child tree and displays a fallback.
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(error: unknown, info: ErrorInfo): void {
    // In production this would forward to an error-reporting service.
    // For the Phase 5 scaffold, a console message is sufficient.
    console.error('Uncaught error in component tree:', error, info);
  }

  override render() {
    if (this.state.hasError) {
      return (
        <Box
          role="alert"
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            py: 8,
            px: 2,
            textAlign: 'center',
          }}
        >
          <Typography variant="h5" component="h2" gutterBottom>
            Something went wrong
          </Typography>
          <Typography variant="body1" color="text.secondary">
            An unexpected error occurred. Please refresh the page or try again later.
          </Typography>
        </Box>
      );
    }

    return this.props.children;
  }
}
