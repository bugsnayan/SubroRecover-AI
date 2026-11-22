import React from 'react';

interface PriorityBadgeProps {
  priority?: 'High' | 'Medium' | 'Low' | string;
  size?: 'sm' | 'md';
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({ priority = 'Medium', size = 'md' }) => {
  const p = priority.toLowerCase();

  const styles = {
    high: 'bg-rust-500/15 text-rust-500 border-rust-500/30 dark:bg-rust-500/20 dark:text-rust-400 dark:border-rust-500/40 shadow-glow-rust',
    medium: 'bg-brass-500/15 text-brass-600 border-brass-500/30 dark:bg-brass-500/20 dark:text-brass-400 dark:border-brass-500/40 shadow-glow-brass',
    low: 'bg-teal-500/15 text-teal-600 border-teal-500/30 dark:bg-teal-500/20 dark:text-teal-400 dark:border-teal-500/40 shadow-glow-teal',
  };

  const currentStyle =
    p === 'high' ? styles.high : p === 'low' ? styles.low : styles.medium;

  const dotColor =
    p === 'high' ? 'bg-rust-500' : p === 'low' ? 'bg-teal-500' : 'bg-brass-500';

  const sizeClasses = size === 'sm' ? 'px-1.5 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-full border transition-all ${sizeClasses} ${currentStyle}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dotColor} animate-pulse`} />
      {priority}
    </span>
  );
};
