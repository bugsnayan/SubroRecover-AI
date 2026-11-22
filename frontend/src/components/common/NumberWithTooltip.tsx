import React, { useState } from 'react';
import { HelpCircle } from 'lucide-react';
import {
  formatCurrency,
  formatCompact,
  formatPercent,
  formatInteger,
} from '../../utils/formatters';

interface NumberWithTooltipProps {
  value: number;
  type?: 'currency' | 'percent' | 'integer' | 'compact';
  label?: string;
  unit?: string;
  tooltip?: string;
  className?: string;
}

export const NumberWithTooltip: React.FC<NumberWithTooltipProps> = ({
  value,
  type = 'currency',
  unit,
  tooltip,
  className = '',
}) => {
  const [showTooltip, setShowTooltip] = useState(false);

  const formatted = (() => {
    if (isNaN(value)) return '—';
    switch (type) {
      case 'currency':
        return formatCurrency(value);
      case 'percent':
        return formatPercent(value);
      case 'compact':
        return formatCompact(value);
      case 'integer':
      default:
        return formatInteger(value);
    }
  })();

  return (
    <span className={`inline-flex items-center gap-1 font-mono tabular-nums ${className}`}>
      <span>{formatted}</span>
      {unit && <span className="text-xs text-slate-400 font-sans ml-0.5">{unit}</span>}
      {tooltip && (
        <span
          className="relative inline-flex items-center cursor-help"
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
        >
          <HelpCircle className="w-3.5 h-3.5 text-slate-400 hover:text-brass-500 transition-colors" />
          {showTooltip && (
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-56 p-2 bg-navy-950/95 dark:bg-navy-950 text-paper-100 text-xs rounded-md shadow-xl border border-navy-700 dark:border-navy-600 z-50 pointer-events-none font-sans font-normal leading-relaxed text-center backdrop-blur-sm">
              {tooltip}
              <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-navy-950" />
            </div>
          )}
        </span>
      )}
    </span>
  );
};
