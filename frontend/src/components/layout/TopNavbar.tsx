import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { Search, Moon, Sun, Bot, Menu } from 'lucide-react';
import { useThemeStore } from '../../stores/themeStore';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../api/client';

interface TopNavbarProps {
  onOpenSearch: () => void;
  onOpenMobileMenu?: () => void;
}

export const TopNavbar: React.FC<TopNavbarProps> = ({ onOpenSearch, onOpenMobileMenu }) => {
  const location = useLocation();
  const { theme, toggleTheme } = useThemeStore();

  const { data: health } = useQuery({
    queryKey: ['system-health'],
    queryFn: () => api.getHealth(),
    refetchInterval: 30000,
  });

  const getPageTitle = (pathname: string) => {
    if (pathname === '/') return 'Executive overview';
    if (pathname.startsWith('/claims/')) return 'Claim investigation dossier';
    if (pathname === '/claims') return 'Subrogation claims ledger';
    if (pathname === '/portfolio') return '3D portfolio risk & opportunity explorer';
    if (pathname === '/assistant') return 'AI subrogation assistant & RAG chat';
    if (pathname === '/reports') return 'Formal investigation reports & PDF generation';
    if (pathname === '/data-quality') return 'Data quality, pipeline health & model performance';
    if (pathname === '/settings') return 'System configuration & thresholds';
    return 'SubroRecover AI';
  };

  const isConnected = health?.database_connected ?? true;

  return (
    <header className="sticky top-0 z-20 w-full h-14 bg-paper-50/90 dark:bg-navy-900/90 backdrop-blur-md border-b border-paper-200 dark:border-navy-800 px-3 sm:px-6 flex items-center justify-between">
      {/* Title / Breadcrumb + Mobile Toggle + Sample Data Badge */}
      <div className="flex items-center gap-2 sm:gap-2.5 min-w-0">
        {onOpenMobileMenu && (
          <button
            onClick={onOpenMobileMenu}
            className="p-1.5 -ml-1 rounded-lg text-slate-500 hover:text-navy-950 dark:hover:text-paper-100 md:hidden"
            aria-label="Open navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}
        <h1 className="text-xs sm:text-base font-bold text-navy-950 dark:text-paper-100 tracking-tight truncate">
          {getPageTitle(location.pathname)}
        </h1>
        <span className="inline-flex items-center gap-1 px-1.5 sm:px-2 py-0.5 rounded-full text-[10px] sm:text-[11px] font-semibold bg-amber-500/15 text-amber-600 dark:text-amber-400 border border-amber-500/30 shrink-0">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
          Sample data
        </span>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-1.5 sm:gap-2.5">
        {/* Ask AI Assistant Button */}
        <Link
          to="/assistant"
          aria-label="Open AI subrogation assistant"
          className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg bg-brass-500/15 hover:bg-brass-500/25 border border-brass-500/40 text-xs font-semibold text-brass-700 dark:text-brass-300 transition-colors shadow-sm"
          title="Ask AI subrogation assistant (cites source evidence)"
        >
          <Bot className="w-3.5 h-3.5 text-brass-600 dark:text-brass-400" />
          <span className="hidden sm:inline">Ask AI</span>
        </Link>

        {/* Quick Search Bar (Command Palette Trigger) */}
        <button
          onClick={onOpenSearch}
          className="flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1.5 rounded-lg bg-paper-100 dark:bg-navy-950 border border-paper-300 dark:border-navy-700 text-xs text-slate-500 dark:text-slate-400 hover:border-brass-500 transition-colors shadow-sm"
        >
          <Search className="w-3.5 h-3.5 text-slate-400" />
          <span className="hidden md:inline">Search claims or jump to...</span>
          <span className="md:hidden">Search</span>
          <kbd className="hidden md:inline-block px-1.5 py-0.5 text-[10px] font-mono bg-paper-200 dark:bg-navy-800 rounded border border-paper-300 dark:border-navy-700 text-slate-500">
            Ctrl+K
          </kbd>
        </button>

        {/* Live API Health Status Indicator */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-medium border bg-paper-100 dark:bg-navy-950 border-paper-300 dark:border-navy-800">
          <span
            className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-teal-500 animate-pulse' : 'bg-rust-500'
            }`}
          />
          <span className="text-[11px] text-slate-600 dark:text-slate-300 hidden lg:inline">
            {isConnected ? 'API LIVE' : 'OFFLINE'}
          </span>
        </div>

        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          className="p-1.5 sm:p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:text-navy-950 dark:hover:text-paper-100 hover:bg-paper-200 dark:hover:bg-navy-800 transition-colors"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} mode`}
        >
          {theme === 'dark' ? (
            <Sun className="w-4 h-4 text-brass-400" />
          ) : (
            <Moon className="w-4 h-4 text-navy-800" />
          )}
        </button>
      </div>
    </header>
  );
};
