import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check } from 'lucide-react';

export interface SelectOption<T> {
  label: string;
  value: T;
}

interface StyledSelectProps<T> {
  value: T;
  options: SelectOption<T>[];
  onChange: (val: T) => void;
  ariaLabel?: string;
  placeholder?: string;
  prefixIcon?: React.ReactNode;
}

export function StyledSelect<T extends string | null>({
  value,
  options,
  onChange,
  ariaLabel,
  placeholder = 'Select option',
  prefixIcon,
}: StyledSelectProps<T>) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const selectedOption = options.find((opt) => opt.value === value) || options[0];

  useEffect(() => {
    const handleOutsideClick = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleOutsideClick);
      document.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      document.removeEventListener('mousedown', handleOutsideClick);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen]);

  const isFiltered = value !== null && value !== '' && value !== undefined;

  return (
    <div ref={containerRef} className="relative inline-block text-left">
      <button
        type="button"
        aria-label={ariaLabel || selectedOption?.label || placeholder}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        onClick={() => setIsOpen((prev) => !prev)}
        className={`flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-md border transition-all shadow-sm focus:outline-none focus:ring-1 focus:ring-brass-500 select-none ${
          isFiltered
            ? 'bg-brass-500/10 border-brass-500 text-brass-700 dark:text-brass-300 font-semibold'
            : 'bg-paper-50 dark:bg-navy-800 border-paper-300 dark:border-navy-700 text-navy-950 dark:text-paper-100 hover:border-paper-400 dark:hover:border-navy-600'
        }`}
      >
        {prefixIcon && <span className="text-slate-400">{prefixIcon}</span>}
        <span className="whitespace-nowrap">{selectedOption?.label || placeholder}</span>
        <ChevronDown
          className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-150 ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </button>

      {isOpen && (
        <div
          role="listbox"
          className="absolute left-0 top-full mt-1.5 min-w-[180px] max-h-60 overflow-y-auto py-1 bg-paper-50 dark:bg-navy-900 border border-paper-300 dark:border-navy-700 rounded-lg shadow-2xl z-50 animate-in fade-in zoom-in-95 duration-100"
        >
          {options.map((option, idx) => {
            const isSelected = option.value === value;
            return (
              <div
                key={idx}
                role="option"
                aria-selected={isSelected}
                onClick={() => {
                  onChange(option.value);
                  setIsOpen(false);
                }}
                className={`flex items-center justify-between px-3 py-1.5 text-xs cursor-pointer transition-colors ${
                  isSelected
                    ? 'bg-brass-500/15 text-brass-700 dark:text-brass-400 font-semibold'
                    : 'text-navy-950 dark:text-paper-100 hover:bg-paper-200/70 dark:hover:bg-navy-800'
                }`}
              >
                <span>{option.label}</span>
                {isSelected && <Check className="w-3.5 h-3.5 text-brass-600 dark:text-brass-400 shrink-0 ml-2" />}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
