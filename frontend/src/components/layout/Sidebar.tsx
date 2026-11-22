import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileSpreadsheet,
  Globe2,
  Bot,
  FileCheck2,
  Cpu,
  Settings,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Building2,
  X,
} from 'lucide-react';

interface SidebarProps {
  isMobile?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isMobile = false, onClose }) => {
  const [collapsed, setCollapsed] = useState(false);

  const navItems = [
    { name: 'Overview', path: '/', icon: LayoutDashboard },
    { name: 'Claims Ledger', path: '/claims', icon: FileSpreadsheet },
    { name: 'Portfolio Explorer', path: '/portfolio', icon: Globe2 },
    { name: 'AI Assistant', path: '/assistant', icon: Bot },
    { name: 'Reports', path: '/reports', icon: FileCheck2 },
    { name: 'Data Quality & Model', path: '/data-quality', icon: Cpu },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <aside
      className={`relative flex flex-col justify-between border-r transition-all duration-300 ease-in-out z-30 ${
        isMobile ? 'w-64 min-h-full' : collapsed ? 'w-20 min-h-screen' : 'w-64 min-h-screen'
      } bg-paper-50 dark:bg-navy-950 border-paper-200 dark:border-navy-800 text-navy-950 dark:text-paper-100`}
    >
      {/* Brand Header */}
      <div>
        <div className="flex items-center justify-between p-4 border-b border-paper-200 dark:border-navy-800">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brass-400 to-brass-600 flex items-center justify-center shadow-glow-brass flex-shrink-0">
              <ShieldCheck className="w-6 h-6 text-navy-950" />
            </div>
            {(!collapsed || isMobile) && (
              <div className="truncate">
                <span className="font-bold text-sm tracking-tight text-navy-950 dark:text-paper-50 block leading-tight">
                  SubroRecover AI
                </span>
                <span className="text-[10px] uppercase font-semibold tracking-wider text-brass-600 dark:text-brass-400 block">
                  Enterprise System
                </span>
              </div>
            )}
          </div>

          {isMobile ? (
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-slate-400 hover:text-navy-950 dark:hover:text-paper-100 hover:bg-paper-200 dark:hover:bg-navy-800 transition-colors"
              title="Close menu"
            >
              <X className="w-5 h-5" />
            </button>
          ) : (
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="p-1 rounded-lg text-slate-400 hover:text-navy-950 dark:hover:text-paper-100 hover:bg-paper-200 dark:hover:bg-navy-800 transition-colors"
              title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
            </button>
          )}
        </div>

        {/* Navigation Items with Real Text Labels */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => {
                  if (isMobile && onClose) {
                    onClose();
                  }
                }}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-brass-500/15 text-brass-600 dark:text-brass-400 border border-brass-500/30 dark:bg-brass-500/20 font-semibold'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-paper-200/60 dark:hover:bg-navy-900 hover:text-navy-950 dark:hover:text-paper-100 border border-transparent'
                  }`
                }
                title={collapsed && !isMobile ? item.name : undefined}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                {(!collapsed || isMobile) && <span className="truncate">{item.name}</span>}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Target Organization & System Status Pill */}
      <div className="p-3 border-t border-paper-200 dark:border-navy-800">
        {!collapsed || isMobile ? (
          <div className="p-3 rounded-xl bg-paper-100 dark:bg-navy-900 border border-paper-300 dark:border-navy-800 text-[11px] space-y-1.5">
            <div className="flex items-center gap-1.5 text-brass-600 dark:text-brass-400 font-semibold">
              <Building2 className="w-3.5 h-3.5" />
              <span>Value Momentum Eval 2027</span>
            </div>
            <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-[10px]">
              <span>Engine</span>
              <span className="font-mono text-teal-600 dark:text-teal-400 font-medium">Multi-Agent RAG</span>
            </div>
            <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-[10px]">
              <span>Database</span>
              <span className="font-mono text-slate-600 dark:text-slate-300 font-medium">SQLite Reconciled</span>
            </div>
          </div>
        ) : (
          <div className="flex justify-center">
            <div
              className="w-2.5 h-2.5 rounded-full bg-teal-500 animate-pulse"
              title="System Online"
            />
          </div>
        )}
      </div>
    </aside>
  );
};
