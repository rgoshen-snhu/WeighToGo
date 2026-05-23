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
      // #00796B is teal-700 from Material Design.  It provides a 4.77:1
      // contrast ratio against white (#ffffff), meeting WCAG 2 AA (4.5:1).
      // The original #00897B (teal-600) only reached 4.31:1 and failed the
      // WCAG AA colour-contrast check.
      main: '#00796B',
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
