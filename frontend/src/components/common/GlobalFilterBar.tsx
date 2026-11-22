import React from 'react';
import { Filter, X, RotateCcw } from 'lucide-react';
import { useFilterStore } from '../../stores/filterStore';
import { StyledSelect } from './StyledSelect';
import { StyledDateRangePicker } from './StyledDateRangePicker';

export const GlobalFilterBar: React.FC = () => {
  const {
    date_from,
    date_to,
    incident_type,
    state,
    priority,
    status,
    setFilter,
    resetFilters,
    activeFilterCount,
  } = useFilterStore();

  const count = activeFilterCount();

  const incidentTypes = [
    { label: 'All incidents', value: null },
    { label: 'Rear-end collision', value: 'Rear-end Collision' },
    { label: 'T-bone / intersection', value: 'T-bone / Intersection Collision' },
    { label: 'Failure to yield', value: 'Failure to Yield' },
    { label: 'Side-swipe collision', value: 'Side-swipe Collision' },
    { label: 'Backing from driveway', value: 'Backing from Driveway' },
    { label: 'Single vehicle impact', value: 'Single Vehicle Impact' },
    { label: 'Hit and run parked', value: 'Hit and Run Parked Vehicle' },
  ];

  const states = [
    { label: 'All states', value: null },
    { label: 'TX (Texas)', value: 'TX' },
    { label: 'CA (California)', value: 'CA' },
    { label: 'FL (Florida)', value: 'FL' },
    { label: 'IL (Illinois)', value: 'IL' },
    { label: 'OH (Ohio)', value: 'OH' },
    { label: 'PA (Pennsylvania)', value: 'PA' },
    { label: 'NY (New York)', value: 'NY' },
    { label: 'GA (Georgia)', value: 'GA' },
    { label: 'NC (North Carolina)', value: 'NC' },
  ];

  const priorities: Array<{ label: string; value: 'High' | 'Medium' | 'Low' | null }> = [
    { label: 'All priorities', value: null },
    { label: 'High priority', value: 'High' },
    { label: 'Medium priority', value: 'Medium' },
    { label: 'Low priority', value: 'Low' },
  ];

  const statuses = [
    { label: 'All statuses', value: null },
    { label: 'Closed recovered', value: 'Closed Recovered' },
    { label: 'Under negotiation', value: 'Under Negotiation' },
    { label: 'Demand sent', value: 'Demand Sent' },
    { label: 'In investigation', value: 'In Investigation' },
    { label: 'Closed no subro', value: 'Closed No Subro' },
  ];

  return (
    <div className="sticky top-0 z-20 w-full bg-paper-100/95 dark:bg-navy-900/95 backdrop-blur-md border-b border-paper-200 dark:border-navy-800 py-2 px-3 -mx-3 mb-4 transition-colors">
      <div className="flex flex-wrap items-center justify-between gap-2.5">
        {/* Left: Custom Styled Dropdown Filters */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-brass-500/10 text-brass-700 dark:text-brass-400 font-medium shrink-0">
            <Filter className="w-3.5 h-3.5" />
            <span>Filters</span>
            {count > 0 && (
              <span className="w-4 h-4 rounded-full bg-brass-500 text-navy-950 text-[10px] flex items-center justify-center font-mono font-bold">
                {count}
              </span>
            )}
          </div>

          {/* Incident Type Styled Dropdown */}
          <StyledSelect
            value={incident_type}
            options={incidentTypes}
            onChange={(val) => setFilter('incident_type', val)}
            placeholder="Incident type"
            ariaLabel="Filter by incident type"
          />

          {/* State Styled Dropdown */}
          <StyledSelect
            value={state}
            options={states}
            onChange={(val) => setFilter('state', val)}
            placeholder="State"
            ariaLabel="Filter by state"
          />

          {/* Priority Styled Dropdown */}
          <StyledSelect
            value={priority}
            options={priorities}
            onChange={(val) => setFilter('priority', val)}
            placeholder="Priority"
            ariaLabel="Filter by priority"
          />

          {/* Status Styled Dropdown */}
          <StyledSelect
            value={status}
            options={statuses}
            onChange={(val) => setFilter('status', val)}
            placeholder="Status"
            ariaLabel="Filter by workflow status"
          />

          {/* Single Styled Date-Range Picker Popover */}
          <StyledDateRangePicker
            startDate={date_from}
            endDate={date_to}
            onChange={(start, end) => {
              setFilter('date_from', start);
              setFilter('date_to', end);
            }}
          />
        </div>

        {/* Right: Active Filter Chips & Clear All Action */}
        {count > 0 && (
          <div className="flex items-center gap-1.5 flex-wrap">
            {incident_type && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-paper-200 dark:bg-navy-800 border border-paper-300 dark:border-navy-700 text-navy-900 dark:text-paper-100">
                <span>{incident_type}</span>
                <button
                  type="button"
                  aria-label="Remove incident type filter"
                  onClick={() => setFilter('incident_type', null)}
                  className="hover:text-rust-500 transition-colors p-0.5"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
            {state && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-paper-200 dark:bg-navy-800 border border-paper-300 dark:border-navy-700 text-navy-900 dark:text-paper-100">
                <span>State: {state}</span>
                <button
                  type="button"
                  aria-label="Remove state filter"
                  onClick={() => setFilter('state', null)}
                  className="hover:text-rust-500 transition-colors p-0.5"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
            {priority && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-paper-200 dark:bg-navy-800 border border-paper-300 dark:border-navy-700 text-navy-900 dark:text-paper-100">
                <span>Priority: {priority}</span>
                <button
                  type="button"
                  aria-label="Remove priority filter"
                  onClick={() => setFilter('priority', null)}
                  className="hover:text-rust-500 transition-colors p-0.5"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
            {status && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-paper-200 dark:bg-navy-800 border border-paper-300 dark:border-navy-700 text-navy-900 dark:text-paper-100">
                <span>Status: {status}</span>
                <button
                  type="button"
                  aria-label="Remove status filter"
                  onClick={() => setFilter('status', null)}
                  className="hover:text-rust-500 transition-colors p-0.5"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
            {(date_from || date_to) && (
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-paper-200 dark:bg-navy-800 border border-paper-300 dark:border-navy-700 text-navy-900 dark:text-paper-100">
                <span>Date: {date_from ?? 'any'} to {date_to ?? 'any'}</span>
                <button
                  type="button"
                  aria-label="Remove date range filter"
                  onClick={() => {
                    setFilter('date_from', null);
                    setFilter('date_to', null);
                  }}
                  className="hover:text-rust-500 transition-colors p-0.5"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}

            <button
              type="button"
              onClick={resetFilters}
              className="flex items-center gap-1 px-2.5 py-0.5 text-xs text-rust-500 hover:text-rust-600 dark:text-rust-400 dark:hover:text-rust-300 font-medium ml-1 transition-colors hover:underline"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Clear all</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
