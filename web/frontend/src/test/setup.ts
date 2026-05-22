import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

// Ensure the DOM is cleaned between every test so stale rendered trees do
// not interfere with subsequent test assertions.
afterEach(() => {
  cleanup();
});
