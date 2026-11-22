import React, { useState } from 'react';
import { ArrowUpRight, ArrowDownRight, Minus, HelpCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useFilterStore } from '../../stores/filterStore';
import {
  formatCurrency,
  formatCompact,
  formatPercent,
  formatInteger,
} from '../../utils/formatters';

interface MetricCardProps {
  title: string;
  value: number;
  type?: 'currency' | 'compactCurrency' | 'percent' | 'integer';
  unit?: string;
  secondaryLine?: React.ReactNode;
  deltaPct?: number | null;
  sentiment?: 'good' | 'bad' | 'neutral';
  comparisonPeriod?: string | null;
  calculation: string;
  sparkline?: number[];
  filterTarget?: { key: 'priority' | 'status'; value: string };
  accentColor?: 'brass' | 'teal' | 'rust' | 'navy';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  type = 'currency',
  unit,
  secondaryLine,
  deltaPct,
  sentiment = 'neutral',
  comparisonPeriod = 'vs previous 30 days',
  calculation,
  sparkline,
  filterTarget,
  accentColor = 'brass',
}) => {
  const navigate = useNavigate();
  const setFilter = useFilterStore((state) => state.setFilter);
  const [showTooltip, setShowTooltip] = useState(false);

  const exactValue = (() => {
    switch (type) {
      case 'compactCurrency':
      case 'currency':
        return formatCurrency(value, { showCents: true });
      case 'percent':
        return formatPercent(value);
      case 'integer':
      default:
        return formatInteger(value);
    }
  })();

  const formattedValue = (() => {
    switch (type) {
      case 'compactCurrency':
        return formatCompact(value);
      case 'currency':
        return formatCurrency(value);
      case 'percent':
        return formatPercent(value);
      case 'integer':
      default:
        return formatInteger(value);
    }
  })();

  const hasDelta = deltaPct !== null && deltaPct !== undefined;
  const isZeroDelta = hasDelta && Math.abs(deltaPct) < 0.05;
  const isUp = hasDelta && deltaPct > 0;

  // Sentiment color styling (good = teal, bad = rust, neutral = slate/brass)
  const deltaBadgeStyle = (() => {
    if (isZeroDelta) {
      return 'text-slate-500 bg-slate-500/10 dark:text-slate-400 dark:bg-slate-500/20';
    }
    if (sentiment === 'good') {
      return 'text-teal-600 bg-teal-500/10 dark:text-teal-400 dark:bg-teal-500/20';
    }
    if (sentiment === 'bad') {
      return 'text-rust-500 bg-rust-500/10 dark:text-rust-400 dark:bg-rust-500/20';
    }
    return 'text-slate-600 bg-slate-500/10 dark:text-slate-300 dark:bg-slate-500/20';
  })();

  // Render SVG Sparkline only when real time-series exists
  const hasSparkline = Boolean(sparkline && sparkline.length >= 2 && sparkline.some((v) => v > 0));
  let sparklinePoints = '';
  const width = 84;
  const height = 26;

  if (hasSparkline && sparkline) {
    const min = Math.min(...sparkline);
    const max = Math.max(...sparkline);
    const range = max - min || 1;
    sparklinePoints = sparkline
      .map((v, i) => {
        const x = (i / (sparkline.length - 1)) * width;
        const y = height - ((v - min) / range) * (height - 6) - 3;
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(' ');
  }

  const strokeColor =
    sentiment === 'good'
      ? '#2F8F89'
      : sentiment === 'bad'
      ? '#D1603D'
      : accentColor === 'teal'
      ? '#2F8F89'
      : accentColor === 'rust'
      ? '#D1603D'
      : '#CFA968';

  const handleClick = () => {
    if (filterTarget) {
      setFilter(filterTarget.key, filterTarget.value);
      navigate('/claims');
    }
  };

  return (
    <div
      onClick={handleClick}
      className={`group relative flex flex-col justify-between h-[116px] p-3 rounded-xl border transition-all duration-200 ${
        filterTarget
          ? 'cursor-pointer hover:border-brass-500 hover:shadow-md focus-visible:ring-2 focus-visible:ring-brass-500'
          : 'hover:border-paper-300 dark:hover:border-navy-600'
      } bg-paper-50 dark:bg-navy-800/85 border-paper-200 dark:border-navy-700/80`}
    >
      {/* Row 1: Sentence-case Label + Help Tooltip + Delta Badge */}
      <div className="flex items-center justify-between gap-1.5 h-5 min-w-0">
        <div className="flex items-center gap-1 min-w-0">
          <span className="text-xs font-medium text-slate-500 dark:text-slate-400 whitespace-nowrap font-sans">
            {title}
          </span>
          <div
            className="relative inline-flex items-center"
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
          >
            <button
              type="button"
              aria-label={`Formula for ${title}`}
              className="text-slate-400 hover:text-brass-500 transition-colors p-0.5"
            >
              <HelpCircle className="w-3 h-3" />
            </button>
            {showTooltip && (
              <div className="absolute left-0 bottom-full mb-2 w-64 p-2.5 bg-navy-950 text-paper-100 text-xs rounded-lg shadow-2xl border border-navy-700 z-50 pointer-events-none font-normal leading-relaxed text-left font-sans">
                <p className="font-semibold text-brass-400 mb-0.5 font-sans">{title}</p>
                <p className="text-paper-100 font-mono text-[11px] mb-1">Exact: {exactValue}</p>
                <p className="text-slate-300 font-sans">{calculation}</p>
                {hasDelta && comparisonPeriod && (
                  <p className="text-[10px] text-slate-400 mt-1 border-t border-navy-800 pt-1 font-sans">
                    Period: {comparisonPeriod}
                  </p>
                )}
                <div className="absolute top-full left-3 border-4 border-transparent border-t-navy-950" />
              </div>
            )}
          </div>
        </div>

        {/* Delta badge with good/bad coloring */}
        {hasDelta && (
          <div
            className={`flex items-center text-[11px] font-mono font-medium px-1.5 py-0.5 rounded shrink-0 ${deltaBadgeStyle}`}
            title={comparisonPeriod || 'vs previous period'}
          >
            {isZeroDelta ? (
              <Minus className="w-3 h-3 mr-0.5" />
            ) : isUp ? (
              <ArrowUpRight className="w-3 h-3 mr-0.5" />
            ) : (
              <ArrowDownRight className="w-3 h-3 mr-0.5" />
            )}
            <span>{isZeroDelta ? '0%' : `${Math.abs(deltaPct)}%`}</span>
          </div>
        )}
      </div>

      {/* Row 2: Value + Unit and Secondary line aligned on fixed baselines */}
      <div className="pt-1 min-w-0">
        <div className="flex items-baseline gap-1 h-8" title={exactValue}>
          <span className="text-xl sm:text-2xl font-bold font-mono tabular-nums tracking-tight text-navy-950 dark:text-paper-50 whitespace-nowrap">
            {formattedValue}
          </span>
          {unit && (
            <span className="text-[11px] font-normal text-slate-500 dark:text-slate-400 font-sans shrink-0">
              {unit}
            </span>
          )}
        </div>
        <div className="text-[11px] font-sans font-medium text-slate-500 dark:text-slate-400 whitespace-nowrap h-4 flex items-center">
          {secondaryLine || '\u00A0'}
        </div>
      </div>
    </div>
  );
};
