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
  // SRS NFR-A-5: every interactive control must meet a 44 × 44 CSS-pixel
  // touch-target floor (DDR-0004). Applied here as targeted overrides on
  // MuiButton and MuiIconButton rather than on MuiButtonBase, because
  // ButtonBase is also the root for Checkbox, Radio, Tab, MenuItem, and
  // similar controls that have their own designed sizing and would visually
  // regress under a blanket 44px floor.
  components: {
    MuiButton: {
      styleOverrides: {
        root: { minHeight: 44, minWidth: 44 },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: { minHeight: 44, minWidth: 44 },
      },
    },
  },
});
