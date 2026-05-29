import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { notifyManager } from '@tanstack/react-query';
import { afterEach, beforeAll } from 'vitest';

// jsdom does not implement ResizeObserver, which Recharts' ResponsiveContainer
// depends on. Provide a no-op polyfill so chart components can mount in tests.
class ResizeObserverStub {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}
globalThis.ResizeObserver ??= ResizeObserverStub as unknown as typeof ResizeObserver;

// Make TanStack Query v5 notify observers synchronously so that synchronous
// act(() => {...}) calls flush cache updates immediately in tests.
beforeAll(() => {
  notifyManager.setScheduler((cb) => cb());
});

// Ensure the DOM is cleaned between every test so stale rendered trees do
// not interfere with subsequent test assertions.
afterEach(() => {
  cleanup();
});
