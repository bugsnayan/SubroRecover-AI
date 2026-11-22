import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Filter,
  Download,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  X,
  ExternalLink,
  Shield,
  Clock,
  DollarSign,
  FileText,
  AlertCircle,
} from 'lucide-react';

import { api } from '../api/client';
import { Claim, ClaimDossier } from '../types';
import { PriorityBadge } from '../components/common/PriorityBadge';
import { StatusBadge } from '../components/common/StatusBadge';
import { NumberWithTooltip } from '../components/common/NumberWithTooltip';
import { formatCurrency, formatPercent, formatInteger } from '../utils/formatters';

export const Claims: React.FC = () => {
  const navigate = useNavigate();

  // Table state
  const [search, setSearchTerm] = useState('');
  const [priorityFilter, setPriorityFilter] = useState<string>('All');
  const [statusFilter, setStatusFilter] = useState<string>('All');
  const [typeFilter, setTypeFilter] = useState<string>('All');
  const [stateFilter, setStateFilter] = useState<string>('All');
  const [sortBy, setSortBy] = useState<string>('incident_date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [page, setPage] = useState<number>(0);
  const pageSize = 15;

  // Drawer state
  const [selectedClaimId, setSelectedClaimId] = useState<string | null>(null);

  // Fetch Claims
  const { data: claims, isLoading } = useQuery({
    queryKey: [
      'claims-list',
      search,
      priorityFilter,
      statusFilter,
      typeFilter,
      stateFilter,
      sortBy,
      sortOrder,
      page,
    ],
    queryFn: () =>
      api.getClaims({
        limit: pageSize,
        offset: page * pageSize,
        search: search || undefined,
        priority: priorityFilter === 'All' ? undefined : priorityFilter,
        subro_status: statusFilter === 'All' ? undefined : statusFilter,
        incident_type: typeFilter === 'All' ? undefined : typeFilter,
        state: stateFilter === 'All' ? undefined : stateFilter,
        sort_by: sortBy,
        sort_order: sortOrder,
      }),
  });

  // Fetch drawer dossier when a row is clicked
  const { data: drawerDossier, isLoading: isDrawerLoading } = useQuery({
    queryKey: ['claim-drawer', selectedClaimId],
    queryFn: () => api.getClaimDossier(selectedClaimId!),
    enabled: !!selectedClaimId,
  });

  const toggleSort = (col: string) => {
    if (sortBy === col) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(col);
      setSortOrder('desc');
    }
  };

  // CSV Export
  const handleExportCSV = () => {
    if (!claims || claims.length === 0) return;
    const headers = [
      'Claim ID',
      'Claim Number',
      'Incident Date',
      'Incident Type',
      'State',
      'Paid Amount',
      'Claimed Amount',
      'Deductible Paid',
      'Status',
      'Priority',
      'Adverse Fault %',
      'Recovery Prob %',
      'Net Recovery Target',
    ];
    const rows = claims.map((c) => [
      c.claim_id,
      c.claim_number,
      c.incident_date,
      `"${c.claim_type}"`,
      c.incident_state,
      c.paid_amount,
      c.claimed_amount,
      c.deductible_paid,
      `"${c.subrogation_status}"`,
      c.priority_level ?? 'Medium',
      c.adverse_fault_pct ?? 75,
      c.recovery_probability ? (c.recovery_probability * 100).toFixed(1) : 75,
      c.net_recovery_estimate ?? 0,
    ]);

    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `subro_claims_export_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Controls Bar */}
      <div className="bg-paper-50 dark:bg-navy-800/90 border border-paper-200 dark:border-navy-700/80 rounded-2xl p-4 shadow-sm backdrop-blur-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* Search Input */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search claim ID, policyholder, location..."
              value={search}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setPage(0);
              }}
              className="w-full pl-9 pr-4 py-2 text-xs rounded-xl bg-paper-100 dark:bg-navy-900 border border-paper-300 dark:border-navy-700 text-navy-950 dark:text-paper-100 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-brass-500"
            />
          </div>

          {/* Quick Filters & CSV Export */}
          <div className="flex flex-wrap items-center gap-2.5">
            <select
              value={priorityFilter}
              onChange={(e) => {
                setPriorityFilter(e.target.value);
                setPage(0);
              }}
              className="text-xs px-2.5 py-2 rounded-xl bg-paper-100 dark:bg-navy-900 border border-paper-300 dark:border-navy-700 text-navy-950 dark:text-paper-100 focus:outline-none focus:ring-1 focus:ring-brass-500"
            >
              <option value="All">All Priorities</option>
              <option value="High">High Priority</option>
              <option value="Medium">Medium Priority</option>
              <option value="Low">Low Priority</option>
            </select>

            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(0);
              }}
              className="text-xs px-2.5 py-2 rounded-xl bg-paper-100 dark:bg-navy-900 border border-paper-300 dark:border-navy-700 text-navy-950 dark:text-paper-100 focus:outline-none focus:ring-1 focus:ring-brass-500"
            >
              <option value="All">All Statuses</option>
              <option value="Identified">Identified</option>
              <option value="Assessed">Assessed</option>
              <option value="Demand Sent">Demand Sent</option>
              <option value="Under Negotiation">Under Negotiation</option>
              <option value="Closed Recovered">Closed Recovered</option>
            </select>

            <button
              onClick={handleExportCSV}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-paper-200 dark:bg-navy-700 hover:bg-brass-500 hover:text-navy-950 text-xs font-semibold transition-colors"
              title="Download CSV of current claims table"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export CSV</span>
            </button>
          </div>
        </div>
      </div>

      {/* Claims Data Table */}
      <div className="bg-paper-50 dark:bg-navy-800/90 border border-paper-200 dark:border-navy-700/80 rounded-2xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-paper-200 dark:border-navy-700/80 bg-paper-100/50 dark:bg-navy-900/50 text-[11px] font-semibold text-slate-500 dark:text-slate-400">
                <th
                  onClick={() => toggleSort('claim_number')}
                  className="py-3 px-4 cursor-pointer hover:text-brass-500 transition-colors"
                >
                  <div className="flex items-center gap-1">
                    <span>Claim reference</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3 px-4">Incident type</th>
                <th
                  onClick={() => toggleSort('paid_amount')}
                  className="py-3 px-4 cursor-pointer hover:text-brass-500 transition-colors"
                >
                  <div className="flex items-center gap-1">
                    <span>Carrier paid</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3 px-4">Adverse fault</th>
                <th
                  onClick={() => toggleSort('recovery_probability')}
                  className="py-3 px-4 cursor-pointer hover:text-brass-500 transition-colors"
                >
                  <div className="flex items-center gap-1">
                    <span>Recovery prob</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">SOL deadline</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-paper-200 dark:divide-navy-700/50 text-xs">
              {isLoading ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400 font-mono">
                    Loading claims ledger data...
                  </td>
                </tr>
              ) : !claims || claims.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400">
                    No claims match your current filter parameters.
                  </td>
                </tr>
              ) : (
                claims.map((claim) => {
                  const prob = claim.recovery_probability ? claim.recovery_probability * 100 : 75;
                  const fault = claim.adverse_fault_pct ?? 75;

                  return (
                    <tr
                      key={claim.claim_id}
                      onClick={() => setSelectedClaimId(claim.claim_id)}
                      className={`hover:bg-paper-100 dark:hover:bg-navy-700/40 cursor-pointer transition-colors ${
                        selectedClaimId === claim.claim_id
                          ? 'bg-brass-500/10 dark:bg-brass-500/15'
                          : ''
                      }`}
                    >
                      {/* Claim ID & Number */}
                      <td className="py-3.5 px-4 font-mono">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-navy-950 dark:text-paper-100">
                            {claim.claim_number}
                          </span>
                          <span className="text-[10px] text-slate-400">({claim.claim_id})</span>
                        </div>
                        <span className="text-[10px] text-slate-500 block">{claim.incident_date}</span>
                      </td>

                      {/* Incident Type & State */}
                      <td className="py-3.5 px-4">
                        <div className="font-medium text-navy-950 dark:text-paper-100">
                          {claim.claim_type}
                        </div>
                        <span className="text-[11px] text-slate-400 font-mono">
                          {claim.incident_location}, {claim.incident_state}
                        </span>
                      </td>

                      {/* Paid Amount */}
                      <td className="py-3.5 px-4 font-mono font-semibold text-navy-950 dark:text-paper-100">
                        {formatCurrency(claim.paid_amount)}
                      </td>

                      {/* Liability % */}
                      <td className="py-3.5 px-4 font-mono font-bold text-rust-500">
                        {fault.toFixed(0)}%
                      </td>

                      {/* Recovery Probability Inline Bar */}
                      <td className="py-3.5 px-4">
                        <div className="w-28">
                          <div className="flex items-center justify-between text-[11px] font-mono mb-1">
                            <span className="font-semibold text-teal-600 dark:text-teal-400">
                              {prob.toFixed(0)}%
                            </span>
                          </div>
                          <div className="w-full h-1.5 bg-paper-300 dark:bg-navy-950 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-teal-500 rounded-full"
                              style={{ width: `${Math.min(100, prob)}%` }}
                            />
                          </div>
                        </div>
                      </td>

                      {/* Priority */}
                      <td className="py-3.5 px-4">
                        <PriorityBadge priority={claim.priority_level ?? 'Medium'} size="sm" />
                      </td>

                      {/* SOL Countdown */}
                      <td className="py-3.5 px-4 font-mono text-[11px] text-slate-500 dark:text-slate-400">
                        {claim.statute_of_limitations_date
                          ? claim.statute_of_limitations_date.slice(0, 10)
                          : '2028-12-31'}
                      </td>

                      {/* Subrogation Status */}
                      <td className="py-3.5 px-4">
                        <StatusBadge status={claim.subrogation_status} />
                      </td>

                      {/* Actions */}
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/claims/${claim.claim_id}`);
                          }}
                          className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-brass-500/10 dark:bg-brass-500/20 text-brass-600 dark:text-brass-400 hover:bg-brass-500 hover:text-navy-950 transition-colors"
                        >
                          View Case
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="p-4 border-t border-paper-200 dark:border-navy-700/80 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
          <span>
            Page {page + 1} • Displaying {claims?.length ?? 0} claims
          </span>
          <div className="flex items-center gap-2">
            <button
              disabled={page === 0}
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              className="p-1.5 rounded-lg border border-paper-300 dark:border-navy-700 hover:bg-paper-200 dark:hover:bg-navy-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              disabled={!claims || claims.length < pageSize}
              onClick={() => setPage((p) => p + 1)}
              className="p-1.5 rounded-lg border border-paper-300 dark:border-navy-700 hover:bg-paper-200 dark:hover:bg-navy-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Right-Side Detail Drawer */}
      {selectedClaimId && (
        <div className="fixed inset-y-0 right-0 w-96 max-w-full bg-paper-50 dark:bg-navy-950 border-l border-paper-300 dark:border-navy-800 shadow-2xl z-40 p-6 flex flex-col justify-between overflow-y-auto animate-in slide-in-from-right duration-250">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-paper-200 dark:border-navy-800">
              <div>
                <span className="text-[10px] font-bold text-brass-500 font-mono">
                  Quick inspection drawer
                </span>
                <h3 className="text-base font-bold text-navy-950 dark:text-paper-100 font-mono mt-0.5">
                  {drawerDossier?.claim.claim_number ?? selectedClaimId}
                </h3>
              </div>
              <button
                onClick={() => setSelectedClaimId(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-navy-950 dark:hover:text-paper-100 hover:bg-paper-200 dark:hover:bg-navy-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {isDrawerLoading ? (
              <div className="py-12 text-center text-xs font-mono text-slate-400">
                Loading dossier details...
              </div>
            ) : drawerDossier ? (
              <div className="mt-4 space-y-4">
                {/* Financial Summary */}
                <div className="p-3.5 rounded-xl bg-paper-100 dark:bg-navy-900 border border-paper-200 dark:border-navy-800 space-y-2 text-xs font-mono">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Carrier Paid Loss:</span>
                    <span className="font-bold text-navy-950 dark:text-paper-100">
                      {formatCurrency(drawerDossier.claim.paid_amount)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Projected Recovery:</span>
                    <span className="font-bold text-teal-600 dark:text-teal-400">
                      {formatCurrency(drawerDossier.assessment?.net_recovery_estimate ?? 0)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Adverse Fault:</span>
                    <span className="font-bold text-rust-500">
                      {(drawerDossier.assessment?.estimated_adverse_fault_pct ?? 80).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Policy Deductible:</span>
                    <span>{formatCurrency(drawerDossier.claim.deductible_paid)}</span>
                  </div>
                </div>

                {/* Priority & Status */}
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">Triage Priority:</span>
                  <PriorityBadge
                    priority={drawerDossier.assessment?.priority_level ?? 'Medium'}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">Workflow Status:</span>
                  <StatusBadge status={drawerDossier.claim.subrogation_status} />
                </div>

                {/* Involved Adverse Party */}
                <div className="p-3 rounded-xl border border-paper-200 dark:border-navy-800 bg-paper-100/50 dark:bg-navy-900/50 text-xs">
                  <span className="text-[10px] font-semibold text-slate-400 block mb-1">
                    Adverse party details
                  </span>
                  {drawerDossier.parties.find((p) => p.party_type.toLowerCase().includes('adverse')) ? (
                    <div className="space-y-1">
                      <p className="font-semibold text-navy-950 dark:text-paper-100">
                        {
                          drawerDossier.parties.find((p) =>
                            p.party_type.toLowerCase().includes('adverse')
                          )?.party_name
                        }
                      </p>
                      <p className="text-slate-400">
                        Carrier:{' '}
                        {
                          drawerDossier.parties.find((p) =>
                            p.party_type.toLowerCase().includes('adverse')
                          )?.insurance_carrier
                        }
                      </p>
                    </div>
                  ) : (
                    <p className="text-slate-400 italic">No adverse party identified yet.</p>
                  )}
                </div>

                {/* Police Report Citations */}
                {drawerDossier.accident_report && (
                  <div className="p-3 rounded-xl border border-paper-200 dark:border-navy-800 bg-paper-100/50 dark:bg-navy-900/50 text-xs">
                    <span className="text-[10px] font-semibold text-slate-400 block mb-1">
                      Enforcement citations
                    </span>
                    <p className="text-rust-500 font-semibold">
                      {drawerDossier.accident_report.citations_issued || 'None issued'}
                    </p>
                  </div>
                )}
              </div>
            ) : null}
          </div>

          <div className="pt-4 border-t border-paper-200 dark:border-navy-800">
            <button
              onClick={() => navigate(`/claims/${selectedClaimId}`)}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-brass-500 hover:bg-brass-600 text-navy-950 font-bold text-xs shadow-glow-brass transition-all"
            >
              <span>Open Full Case Dossier</span>
              <ExternalLink className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
