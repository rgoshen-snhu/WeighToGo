import { createTheme } from '@mui/material/styles';

/**
 * The Weigh to Go! Material UI theme.
 *
 * The color palette is the design-system specification carried forward from
 * the original artifact: a teal primary identity with standard semantic
 * colors for success, warning, and error states.
 */
export const theme = createTheme({
  palette: {
    primary: {
      main: '#00897B',
      dark: '#00695C',
      light: '#4DB6AC',
    },
    success: { main: '#4CAF50' },
    warning: { main: '#FF9800' },
    error: { main: '#F44336' },
    background: { default: '#F5F5F5' },
    text: {
      primary: '#212121',
      secondary: '#757575',
    },
  },
});
