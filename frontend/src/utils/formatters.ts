/**
 * SubroRecover AI - Shared Number & Currency Formatter Module
 * Enforces strict en-US grouping (no Indian grouping like $2,03,966 -> $203,966)
 * and eliminates stray decimals ($248,217.93 -> $248,218).
 */

const EN_US_LOCALE = 'en-US';

export interface FormatCurrencyOptions {
  decimals?: number; // default: 0
  showCents?: boolean; // alias for decimals: 2
  compact?: boolean;
}

/**
 * Formats a number as standard USD with en-US comma grouping.
 * Defaults to 0 decimal places to eliminate stray cents ($248,217.93 -> $248,218).
 */
export function formatCurrency(
  val: number | string | null | undefined,
  options?: FormatCurrencyOptions
): string {
  if (val === null || val === undefined || val === '') {
    return '$0';
  }

  const num = typeof val === 'string' ? parseFloat(val) : val;
  if (isNaN(num)) {
    return '$0';
  }

  if (options?.compact) {
    return formatCompact(num);
  }

  const decimals = options?.decimals ?? (options?.showCents ? 2 : 0);

  return new Intl.NumberFormat(EN_US_LOCALE, {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num);
}

/**
 * Formats a currency amount into compact notation:
 * >= $1,000,000 -> "$4.49M"
 * >= $1,000     -> "$248K", "$775K", "$204K"
 * < $1,000      -> "$250"
 */
export function formatCompact(val: number | string | null | undefined): string {
  if (val === null || val === undefined || val === '') {
    return '$0';
  }

  const num = typeof val === 'string' ? parseFloat(val) : val;
  if (isNaN(num)) {
    return '$0';
  }

  const abs = Math.abs(num);
  const sign = num < 0 ? '-' : '';

  if (abs >= 1_000_000) {
    const formatted = (abs / 1_000_000).toFixed(2).replace(/\.?0+$/, '');
    return `${sign}$${formatted}M`;
  }
  if (abs >= 1_000) {
    return `${sign}$${Math.round(abs / 1_000)}K`;
  }
  return `${sign}$${Math.round(abs)}`;
}

/**
 * Formats a percentage value with en-US notation.
 * e.g. 40.50 -> "40.5%", 100 -> "100%" (when decimals: 0)
 */
export function formatPercent(
  val: number | string | null | undefined,
  options?: { decimals?: number }
): string {
  if (val === null || val === undefined || val === '') {
    return '0%';
  }

  const num = typeof val === 'string' ? parseFloat(val) : val;
  if (isNaN(num)) {
    return '0%';
  }

  const decimals = options?.decimals ?? 1;
  return `${num.toFixed(decimals)}%`;
}

/**
 * Formats a whole integer with en-US comma grouping.
 * e.g. 180 -> "180", 2500 -> "2,500"
 */
export function formatInteger(val: number | string | null | undefined): string {
  if (val === null || val === undefined || val === '') {
    return '0';
  }

  const num = typeof val === 'string' ? parseFloat(val) : val;
  if (isNaN(num)) {
    return '0';
  }

  return new Intl.NumberFormat(EN_US_LOCALE, {
    maximumFractionDigits: 0,
  }).format(Math.round(num));
}
