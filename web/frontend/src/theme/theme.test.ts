import { describe, expect, it } from 'vitest';

import { theme } from './theme';

describe('theme', () => {
  it('applies the Weigh to Go! design-system color palette', () => {
    // #00796B (teal-700) provides 4.77:1 contrast vs white, meeting WCAG AA.
    expect(theme.palette.primary.main).toBe('#00796B');
    expect(theme.palette.primary.dark).toBe('#00695C');
    expect(theme.palette.primary.light).toBe('#4DB6AC');
    expect(theme.palette.success.main).toBe('#4CAF50');
    expect(theme.palette.warning.main).toBe('#FF9800');
    expect(theme.palette.error.main).toBe('#F44336');
    expect(theme.palette.background.default).toBe('#F5F5F5');
    expect(theme.palette.text.primary).toBe('#212121');
    expect(theme.palette.text.secondary).toBe('#757575');
  });
});
