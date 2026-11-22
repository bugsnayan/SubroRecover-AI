import React, { useState, useRef, useEffect } from 'react';
import { Calendar, ChevronDown, X, Check } from 'lucide-react';

interface StyledDateRangePickerProps {
  startDate: string | null;
  endDate: string | null;
  onChange: (start: string | null, end: string | null) => void;
}

const PRESETS = [
  { label: 'All dates', start: null, end: null },
  { label: 'Last 30 days', start: '2025-12-01', end: '2025-12-31' },
  { label: 'Last 90 days', start: '2025-10-01', end: '2025-12-31' },
  { label: 'Q3 2025', start: '2025-07-01', end: '2025-09-30' },
  { label: 'Q4 2025', start: '2025-10-01', end: '2025-12-31' },
  { label: 'Full year 2025', start: '2025-01-01', end: '2025-12-31' },
];

export const StyledDateRangePicker: React.FC<StyledDateRangePickerProps> = ({
  startDate,
  endDate,
  onChange,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [customStart, setCustomStart] = useState(startDate || '');
  const [customEnd, setCustomEnd] = useState(endDate || '');
  const containerRef = useRef<HTMLDivElement>(null);

  // Sync internal state when external props change
  useEffect(() => {
    setCustomStart(startDate || '');
    setCustomEnd(endDate || '');
  }, [startDate, endDate]);

  // Click outside to close
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  // Handle Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsOpen(false);
    };
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
    }
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  const hasFilter = Boolean(startDate || endDate);

  const formatButtonLabel = () => {
    if (!startDate && !endDate) return 'Date range';
    if (startDate && endDate) {
      return `${startDate} – ${endDate}`;
    }
    if (startDate) return `From ${startDate}`;
    return `To ${endDate}`;
  };

  const handleApplyCustom = () => {
    onChange(customStart || null, customEnd || null);
    setIsOpen(false);
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange(null, null);
    setCustomStart('');
    setCustomEnd('');
  };

  return (
    <div className="relative inline-block" ref={containerRef}>
      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-haspopup="dialog"
        aria-label="Filter by date range"
        className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-all shadow-sm ${
          hasFilter
            ? 'bg-brass-500/15 border border-brass-500/40 text-brass-700 dark:text-brass-300 font-semibold'
            : 'bg-paper-50 dark:bg-navy-800 border border-paper-300 dark:border-navy-700 text-navy-950 dark:text-paper-100 hover:border-brass-500/60'
        }`}
      >
        <Calendar className={`w-3.5 h-3.5 ${hasFilter ? 'text-brass-600 dark:text-brass-400' : 'text-slate-400'}`} />
        <span className={hasFilter ? 'font-mono text-[11px]' : 'font-sans'}>
          {formatButtonLabel()}
        </span>
        {hasFilter ? (
          <span
            onClick={handleClear}
            className="p-0.5 hover:text-rust-500 transition-colors ml-0.5 rounded cursor-pointer"
            title="Clear date range"
          >
            <X className="w-3 h-3" />
          </span>
        ) : (
          <ChevronDown className="w-3 h-3 text-slate-400" />
        )}
      </button>

      {/* Styled Popover Dropdown */}
      {isOpen && (
        <div className="absolute left-0 mt-1.5 w-72 p-3 bg-paper-50 dark:bg-navy-900 border border-paper-300 dark:border-navy-700 rounded-xl shadow-2xl z-50 animate-in fade-in zoom-in-95 duration-150">
          <div className="text-[11px] font-bold text-navy-950 dark:text-paper-100 mb-2 font-sans flex items-center justify-between">
            <span>Select date range</span>
            {hasFilter && (
              <button
                type="button"
                onClick={handleClear}
                className="text-[10px] text-rust-500 hover:underline font-normal font-sans"
              >
                Reset
              </button>
            )}
          </div>

          {/* Quick Presets Grid */}
          <div className="grid grid-cols-2 gap-1.5 mb-3">
            {PRESETS.map((p) => {
              const isSelected =
                (p.start === null && !startDate && !endDate) ||
                (p.start === startDate && p.end === endDate);
              return (
                <button
                  key={p.label}
                  type="button"
                  onClick={() => {
                    onChange(p.start, p.end);
                    setIsOpen(false);
                  }}
                  className={`px-2 py-1.5 rounded-lg text-xs font-sans text-left flex items-center justify-between transition-colors ${
                    isSelected
                      ? 'bg-brass-500/20 text-brass-700 dark:text-brass-300 font-semibold border border-brass-500/40'
                      : 'bg-paper-100 dark:bg-navy-800 text-slate-700 dark:text-slate-300 hover:bg-paper-200 dark:hover:bg-navy-700'
                  }`}
                >
                  <span className="truncate">{p.label}</span>
                  {isSelected && <Check className="w-3 h-3 text-brass-500 shrink-0" />}
                </button>
              );
            })}
          </div>

          {/* Custom Date Range Inputs */}
          <div className="pt-2.5 border-t border-paper-200 dark:border-navy-800 space-y-2">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block font-sans">
              Custom range
            </span>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <label className="text-[10px] text-slate-500 block mb-0.5 font-sans">Start</label>
                <input
                  type="text"
                  placeholder="YYYY-MM-DD"
                  value={customStart}
                  onChange={(e) => setCustomStart(e.target.value)}
                  className="w-full px-2 py-1 rounded bg-paper-100 dark:bg-navy-800 border border-paper-300 dark:border-navy-700 text-navy-950 dark:text-paper-100 font-mono text-[11px] focus:outline-none focus:border-brass-500"
                />
              </div>
              <div>
                <label className="text-[10px] text-slate-500 block mb-0.5 font-sans">End</label>
                <input
                  type="text"
                  placeholder="YYYY-MM-DD"
                  value={customEnd}
                  onChange={(e) => setCustomEnd(e.target.value)}
                  className="w-full px-2 py-1 rounded bg-paper-100 dark:bg-navy-800 border border-paper-300 dark:border-navy-700 text-navy-950 dark:text-paper-100 font-mono text-[11px] focus:outline-none focus:border-brass-500"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-1.5 pt-1">
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="px-2.5 py-1 text-xs text-slate-500 hover:text-navy-950 dark:hover:text-paper-100 font-sans"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleApplyCustom}
                className="px-3 py-1 rounded bg-brass-500 hover:bg-brass-600 text-navy-950 font-bold text-xs font-sans shadow-sm transition-colors"
              >
                Apply
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
