import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, FileText, BarChart3, Database, MessageSquare, Shield, X, ArrowRight } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../api/client';
import { formatCurrency } from '../../utils/formatters';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
        else {
          // Open handled by parent or toggle
        }
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const { data: claims } = useQuery({
    queryKey: ['palette-claims', searchTerm],
    queryFn: () => api.getClaims({ search: searchTerm, limit: 6 }),
    enabled: isOpen && searchTerm.length >= 2,
  });

  if (!isOpen) return null;

  const quickPages = [
    { name: 'Executive Overview', path: '/', icon: BarChart3, desc: '6 KPIs, Funnel & Exposure' },
    { name: 'Claims Table', path: '/claims', icon: FileText, desc: 'Search & Multi-Filter Ledger' },
    { name: 'Portfolio 3D Explorer', path: '/portfolio', icon: Database, desc: 'Multi-variable 3D Cluster' },
    { name: 'AI Assistant', path: '/assistant', icon: MessageSquare, desc: 'RAG Evidence Reasoning Chat' },
    { name: 'Investigation Reports', path: '/reports', icon: Shield, desc: 'Compiled PDF Artifacts' },
    { name: 'Data Quality & Model', path: '/data-quality', icon: Database, desc: 'Confusion Matrix & Pipeline' },
  ];

  const handleSelect = (path: string) => {
    navigate(path);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-navy-950/70 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-2xl bg-paper-50 dark:bg-navy-900 border border-paper-300 dark:border-navy-700 rounded-2xl shadow-2xl overflow-hidden">
        {/* Search Input Bar */}
        <div className="relative flex items-center px-4 py-3 border-b border-paper-200 dark:border-navy-700">
          <Search className="w-5 h-5 text-slate-400 mr-3" />
          <input
            type="text"
            autoFocus
            placeholder="Type a claim number (e.g. CLM-0001) or page name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-transparent text-sm text-navy-950 dark:text-paper-100 placeholder-slate-400 focus:outline-none"
          />
          <button
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-navy-950 dark:hover:text-paper-100 hover:bg-paper-200 dark:hover:bg-navy-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Results */}
        <div className="p-3 max-h-96 overflow-y-auto space-y-4">
          {/* Claim Results if searching */}
          {searchTerm.length >= 2 && claims && claims.length > 0 && (
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-3 mb-1">
                Matching Insurance Claims
              </p>
              <div className="space-y-1">
                {claims.map((c) => (
                  <div
                    key={c.claim_id}
                    onClick={() => handleSelect(`/claims/${c.claim_id}`)}
                    className="flex items-center justify-between p-2.5 rounded-lg hover:bg-brass-500/10 dark:hover:bg-brass-500/15 cursor-pointer transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-md bg-paper-200 dark:bg-navy-800 flex items-center justify-center text-xs font-mono font-bold text-brass-600 dark:text-brass-400">
                        {c.incident_state}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-xs text-navy-950 dark:text-paper-100 font-mono">
                            {c.claim_number}
                          </span>
                          <span className="text-[11px] text-slate-400">({c.claim_id})</span>
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400">{c.claim_type}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-xs font-semibold text-navy-950 dark:text-paper-100">
                        {formatCurrency(c.paid_amount)}
                      </span>
                      <ArrowRight className="w-4 h-4 text-slate-400" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quick Page Navigation */}
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-3 mb-1">
              Navigation & Workspaces
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
              {quickPages.map((page) => {
                const Icon = page.icon;
                return (
                  <div
                    key={page.path}
                    onClick={() => handleSelect(page.path)}
                    className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-paper-200/70 dark:hover:bg-navy-800/80 cursor-pointer transition-colors"
                  >
                    <div className="w-7 h-7 rounded-md bg-paper-200 dark:bg-navy-700/80 flex items-center justify-center text-brass-600 dark:text-brass-400">
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-xs font-medium text-navy-950 dark:text-paper-100">
                        {page.name}
                      </p>
                      <p className="text-[11px] text-slate-400">{page.desc}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Footer Shortcut Helper */}
        <div className="px-4 py-2 bg-paper-100 dark:bg-navy-950/80 border-t border-paper-200 dark:border-navy-700/60 flex items-center justify-between text-[11px] text-slate-400">
          <span>Press ESC to close</span>
          <span>SubroRecover AI Navigation Hub</span>
        </div>
      </div>
    </div>
  );
};
