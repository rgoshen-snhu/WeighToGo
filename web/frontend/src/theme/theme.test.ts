import { describe, expect, it } from 'vitest';

import { theme } from './theme';

describe('theme', () => {
  it('applies the Weigh to Go! design-system color palette', () => {
    expect(theme.palette.primary.main).toBe('#00897B');
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
