import React from 'react';

interface StatusBadgeProps {
  status: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const getStyle = (s: string) => {
    const lower = s.toLowerCase();
    if (lower.includes('recovered') || lower.includes('closed recovered')) {
      return 'bg-teal-500/15 text-teal-600 border-teal-500/30 dark:bg-teal-500/20 dark:text-teal-400';
    }
    if (lower.includes('demand') || lower.includes('sent')) {
      return 'bg-brass-500/15 text-brass-600 border-brass-500/30 dark:bg-brass-500/20 dark:text-brass-400';
    }
    if (lower.includes('negotiating') || lower.includes('negotiation')) {
      return 'bg-rust-500/15 text-rust-500 border-rust-500/30 dark:bg-rust-500/20 dark:text-rust-400';
    }
    if (lower.includes('assessed')) {
      return 'bg-blue-500/15 text-blue-600 border-blue-500/30 dark:bg-blue-500/20 dark:text-blue-400';
    }
    return 'bg-slate-500/15 text-slate-600 border-slate-500/30 dark:bg-slate-500/20 dark:text-slate-300';
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${getStyle(
        status
      )}`}
    >
      {status}
    </span>
  );
};
