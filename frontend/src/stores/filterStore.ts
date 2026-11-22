import { create } from 'zustand';

export interface FilterState {
  date_from: string | null;
  date_to: string | null;
  incident_type: string | null;
  state: string | null;
  priority: 'High' | 'Medium' | 'Low' | null;
  status: string | null;
  search: string;
  setFilter: <K extends keyof Omit<FilterState, 'setFilter' | 'resetFilters' | 'activeFilterCount'>>(
    key: K,
    value: FilterState[K]
  ) => void;
  resetFilters: () => void;
  activeFilterCount: () => number;
}

export const useFilterStore = create<FilterState>((set, get) => ({
  date_from: null,
  date_to: null,
  incident_type: null,
  state: null,
  priority: null,
  status: null,
  search: '',
  setFilter: (key, value) => set({ [key]: value }),
  resetFilters: () =>
    set({
      date_from: null,
      date_to: null,
      incident_type: null,
      state: null,
      priority: null,
      status: null,
      search: '',
    }),
  activeFilterCount: () => {
    const s = get();
    let count = 0;
    if (s.date_from) count++;
    if (s.date_to) count++;
    if (s.incident_type) count++;
    if (s.state) count++;
    if (s.priority) count++;
    if (s.status) count++;
    if (s.search) count++;
    return count;
  },
}));
