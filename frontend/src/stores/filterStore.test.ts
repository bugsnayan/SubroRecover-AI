import { describe, it, expect, beforeEach } from 'vitest';
import { useFilterStore } from './filterStore';

describe('Filter Store (Zustand)', () => {
  beforeEach(() => {
    useFilterStore.getState().resetFilters();
  });

  it('initializes with default empty filters', () => {
    const state = useFilterStore.getState();
    expect(state.date_from).toBeNull();
    expect(state.date_to).toBeNull();
    expect(state.incident_type).toBeNull();
    expect(state.state).toBeNull();
    expect(state.priority).toBeNull();
    expect(state.status).toBeNull();
    expect(state.search).toBe('');
    expect(state.activeFilterCount()).toBe(0);
  });

  it('updates individual filters and increments activeFilterCount', () => {
    useFilterStore.getState().setFilter('priority', 'High');
    expect(useFilterStore.getState().priority).toBe('High');
    expect(useFilterStore.getState().activeFilterCount()).toBe(1);

    useFilterStore.getState().setFilter('state', 'CA');
    expect(useFilterStore.getState().state).toBe('CA');
    expect(useFilterStore.getState().activeFilterCount()).toBe(2);

    useFilterStore.getState().setFilter('search', 'Rear-end');
    expect(useFilterStore.getState().search).toBe('Rear-end');
    expect(useFilterStore.getState().activeFilterCount()).toBe(3);
  });

  it('resets all filters back to default values', () => {
    useFilterStore.getState().setFilter('priority', 'Medium');
    useFilterStore.getState().setFilter('incident_type', 'Intersection');
    useFilterStore.getState().setFilter('search', 'CLM-001');
    expect(useFilterStore.getState().activeFilterCount()).toBe(3);

    useFilterStore.getState().resetFilters();
    const state = useFilterStore.getState();
    expect(state.priority).toBeNull();
    expect(state.incident_type).toBeNull();
    expect(state.search).toBe('');
    expect(state.activeFilterCount()).toBe(0);
  });
});
