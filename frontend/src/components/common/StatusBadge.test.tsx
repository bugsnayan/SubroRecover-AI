import { describe, it, expect } from 'vitest';
import { StatusBadge } from './StatusBadge';

describe('StatusBadge component', () => {
  it('is properly defined as a React component', () => {
    expect(StatusBadge).toBeDefined();
    expect(typeof StatusBadge).toBe('function');
  });
});
