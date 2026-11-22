import { describe, it, expect } from 'vitest';
import {
  formatCurrency,
  formatCompact,
  formatPercent,
  formatInteger,
} from './formatters';

describe('Shared Number & Currency Formatters', () => {
  describe('formatCurrency', () => {
    it('enforces standard en-US 3-digit comma grouping (no Indian grouping like $2,03,966)', () => {
      // 203966 in en-IN is "$2,03,966", but must strictly be "$203,966"
      expect(formatCurrency(203966)).toBe('$203,966');
      expect(formatCurrency(203966.1)).toBe('$203,966');
      expect(formatCurrency(4486249.06)).toBe('$4,486,249');
    });

    it('eliminates stray decimals by default ($248,217.93 -> $248,218)', () => {
      expect(formatCurrency(248217.93)).toBe('$248,218');
      expect(formatCurrency(140995.99)).toBe('$140,996');
      expect(formatCurrency(85621.66)).toBe('$85,622');
    });

    it('supports 2 decimal places when explicitly requested with showCents or decimals: 2', () => {
      expect(formatCurrency(4486249.06, { showCents: true })).toBe('$4,486,249.06');
      expect(formatCurrency(248217.93, { decimals: 2 })).toBe('$248,217.93');
    });

    it('handles zero, null, undefined, and empty string safely', () => {
      expect(formatCurrency(0)).toBe('$0');
      expect(formatCurrency(null)).toBe('$0');
      expect(formatCurrency(undefined)).toBe('$0');
      expect(formatCurrency('')).toBe('$0');
    });
  });

  describe('formatCompact', () => {
    it('formats values >= 1M into compact millions ($4.49M)', () => {
      expect(formatCompact(4486249.06)).toBe('$4.49M');
      expect(formatCompact(1000000)).toBe('$1M');
      expect(formatCompact(2500000)).toBe('$2.5M');
    });

    it('formats values >= 1K into compact thousands ($248K, $775K, $204K)', () => {
      expect(formatCompact(248217.93)).toBe('$248K');
      expect(formatCompact(775422.88)).toBe('$775K');
      expect(formatCompact(203966.1)).toBe('$204K');
      expect(formatCompact(85621.66)).toBe('$86K');
    });

    it('formats sub-thousand values accurately', () => {
      expect(formatCompact(750)).toBe('$750');
      expect(formatCompact(0)).toBe('$0');
    });
  });

  describe('formatPercent', () => {
    it('formats percentages with standard single decimal by default', () => {
      expect(formatPercent(40.5)).toBe('40.5%');
      expect(formatPercent(17.28)).toBe('17.3%');
      expect(formatPercent(4.54)).toBe('4.5%');
    });

    it('formats whole-number percentages when decimals: 0 is specified', () => {
      expect(formatPercent(100, { decimals: 0 })).toBe('100%');
      expect(formatPercent(40.5, { decimals: 0 })).toBe('41%');
    });

    it('handles null, undefined, and zero safely', () => {
      expect(formatPercent(0)).toBe('0.0%');
      expect(formatPercent(null)).toBe('0%');
      expect(formatPercent(undefined)).toBe('0%');
    });
  });

  describe('formatInteger', () => {
    it('formats whole integers with en-US grouping', () => {
      expect(formatInteger(180)).toBe('180');
      expect(formatInteger(27)).toBe('27');
      expect(formatInteger(2500)).toBe('2,500');
    });

    it('handles null and undefined safely', () => {
      expect(formatInteger(0)).toBe('0');
      expect(formatInteger(null)).toBe('0');
      expect(formatInteger(undefined)).toBe('0');
    });
  });
});
