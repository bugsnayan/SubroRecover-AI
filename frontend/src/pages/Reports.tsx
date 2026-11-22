import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  Download,
  Plus,
  Eye,
  CheckCircle2,
  Clock,
  ExternalLink,
  Shield,
  X,
  FileCheck2,
} from 'lucide-react';

import { api } from '../api/client';
import { ReportItem } from '../types';
import { PriorityBadge } from '../components/common/PriorityBadge';
import { formatCurrency } from '../utils/formatters';

export const Reports: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Modal State for Generating New Report
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [targetClaimId, setTargetClaimId] = useState('CLM-0001');
  const [reportScope, setReportScope] = useState('Comprehensive Multi-Agent Audit');
  const [reportNotes, setReportNotes] = useState('');

  // Report Preview Modal State
  const [previewReport, setPreviewReport] = useState<any | null>(null);

  // 1. Fetch Reports List
  const { data: reports, isLoading } = useQuery({
    queryKey: ['reports-list'],
    queryFn: () => api.getReports(50),
  });

  // 2. Fetch Claims for the dropdown
  const { data: claims } = useQuery({
    queryKey: ['report-claims-select'],
    queryFn: () => api.getClaims({ limit: 100 }),
    enabled: isModalOpen,
  });

  // Generate Report Mutation
  const generateMutation = useMutation({
    mutationFn: (payload: { claim_id: string; scope: string; notes: string }) =>
      api.generateReport(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports-list'] });
      setIsModalOpen(false);
      setReportNotes('');
    },
  });

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault();
    generateMutation.mutate({
      claim_id: targetClaimId,
      scope: reportScope,
      notes: reportNotes,
    });
  };

  const openPreview = async (reportId: string) => {
    const detail = await api.getReportDetail(reportId);
    setPreviewReport(detail);
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header Bar */}
      <div className="bg-paper-50 dark:bg-navy-800/90 border border-paper-200 dark:border-navy-700/80 rounded-2xl p-5 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <FileCheck2 className="w-5 h-5 text-brass-500" />
            <h2 className="text-base font-bold text-navy-950 dark:text-paper-100 tracking-tight">
              Subrogation Investigation Reports & PDF Exports
            </h2>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Formal, court-ready 14-section investigation packages compiled via ReportLab PDF engine
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-brass-500 hover:bg-brass-600 text-navy-950 font-bold text-xs shadow-glow-brass transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Generate New Report</span>
        </button>
      </div>

      {/* Reports Table */}
      <div className="bg-paper-50 dark:bg-navy-800/90 border border-paper-200 dark:border-navy-700/80 rounded-2xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-paper-200 dark:border-navy-700/80 bg-paper-100/50 dark:bg-navy-900/50 text-[11px] font-semibold text-slate-500 dark:text-slate-400">
                <th className="py-3 px-4">Report number</th>
                <th className="py-3 px-4">Claim reference</th>
                <th className="py-3 px-4">Incident type</th>
                <th className="py-3 px-4">Net recovery</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">Generated date</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-paper-200 dark:divide-navy-700/50 text-xs">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400 font-mono">
                    Loading generated reports...
                  </td>
                </tr>
              ) : !reports || reports.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    No reports generated yet. Click "Generate New Report" to compile one.
                  </td>
                </tr>
              ) : (
                reports.map((rpt) => (
                  <tr
                    key={rpt.report_id}
                    className="hover:bg-paper-100 dark:hover:bg-navy-700/40 transition-colors"
                  >
                    {/* Report Number */}
                    <td className="py-3.5 px-4 font-mono font-bold text-navy-950 dark:text-paper-100">
                      {rpt.report_number}
                    </td>

                    {/* Claim Reference */}
                    <td className="py-3.5 px-4 font-mono">
                      <button
                        onClick={() => navigate(`/claims/${rpt.claim_id}`)}
                        className="text-brass-600 dark:text-brass-400 hover:underline font-semibold"
                      >
                        {rpt.claim_number}
                      </button>
                    </td>

                    {/* Incident Type */}
                    <td className="py-3.5 px-4 text-slate-600 dark:text-slate-300">
                      {rpt.incident_type}
                    </td>

                    {/* Net Recovery */}
                    <td className="py-3.5 px-4 font-mono font-bold text-teal-600 dark:text-teal-400">
                      {formatCurrency(rpt.net_recovery)}
                    </td>

                    {/* Priority */}
                    <td className="py-3.5 px-4">
                      <PriorityBadge priority={rpt.priority} size="sm" />
                    </td>

                    {/* Date */}
                    <td className="py-3.5 px-4 font-mono text-slate-400 text-[11px]">
                      {rpt.created_at ? rpt.created_at.slice(0, 10) : '2026-02-18'}
                    </td>

                    {/* Actions */}
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => openPreview(rpt.report_id)}
                          className="p-1.5 rounded-lg border border-paper-300 dark:border-navy-700 hover:bg-paper-200 dark:hover:bg-navy-800 text-slate-500 hover:text-navy-950 dark:hover:text-paper-100 transition-colors"
                          title="Preview Report Details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <a
                          href={rpt.download_url}
                          target="_blank"
                          rel="noreferrer"
                          className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-brass-500 hover:bg-brass-600 text-navy-950 font-bold text-[11px] transition-all"
                        >
                          <Download className="w-3.5 h-3.5" />
                          <span>PDF</span>
                        </a>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal: Generate New Report */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/70 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="w-full max-w-lg bg-paper-50 dark:bg-navy-900 border border-paper-300 dark:border-navy-700 rounded-2xl shadow-2xl p-6">
            <div className="flex items-center justify-between pb-3 border-b border-paper-200 dark:border-navy-800">
              <h3 className="text-sm font-bold text-navy-950 dark:text-paper-100">
                Generate Subrogation Investigation Report
              </h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1 text-slate-400 hover:text-navy-950 dark:hover:text-paper-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleGenerate} className="mt-4 space-y-4 text-xs">
              <div>
                <label className="block text-slate-500 dark:text-slate-400 font-semibold mb-1">
                  Target Insurance Claim
                </label>
                <select
                  value={targetClaimId}
                  onChange={(e) => setTargetClaimId(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-paper-100 dark:bg-navy-950 border border-paper-300 dark:border-navy-700 text-navy-950 dark:text-paper-100 focus:outline-none focus:ring-1 focus:ring-brass-500"
                >
                  {claims?.map((c) => (
                    <option key={c.claim_id} value={c.claim_id}>
                      {c.claim_number} ({c.claim_id}) — {c.claim_type} ({formatCurrency(c.paid_amount)})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-500 dark:text-slate-400 font-semibold mb-1">
                  Audit Scope
                </label>
                <select
                  value={reportScope}
                  onChange={(e) => setReportScope(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-paper-100 dark:bg-navy-950 border border-paper-300 dark:border-navy-700 text-navy-950 dark:text-paper-100 focus:outline-none focus:ring-1 focus:ring-brass-500"
                >
                  <option value="Comprehensive Multi-Agent Audit">Comprehensive Multi-Agent Audit</option>
                  <option value="Executive Summary & Demand Package">Executive Summary & Demand Package</option>
                  <option value="Litigation Readiness & Evidentiary Dossier">Litigation Readiness & Evidentiary Dossier</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-500 dark:text-slate-400 font-semibold mb-1">
                  Investigator Notes & Statutory Citations
                </label>
                <textarea
                  rows={3}
                  placeholder="Optional adjuster notes or statutory citations to include in the final report..."
                  value={reportNotes}
                  onChange={(e) => setReportNotes(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-paper-100 dark:bg-navy-950 border border-paper-300 dark:border-navy-700 text-navy-950 dark:text-paper-100 focus:outline-none focus:ring-1 focus:ring-brass-500"
                />
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-slate-400 hover:bg-paper-200 dark:hover:bg-navy-800 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={generateMutation.isPending}
                  className="px-5 py-2 rounded-xl bg-brass-500 hover:bg-brass-600 disabled:opacity-40 text-navy-950 font-bold shadow-glow-brass"
                >
                  {generateMutation.isPending ? 'Compiling PDF...' : 'Compile & Generate PDF'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Report Details Preview */}
      {previewReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/70 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="w-full max-w-2xl bg-paper-50 dark:bg-navy-900 border border-paper-300 dark:border-navy-700 rounded-2xl shadow-2xl p-6 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-paper-200 dark:border-navy-800">
              <div>
                <span className="text-[10px] font-mono text-brass-500 font-bold uppercase">
                  {previewReport.report_number}
                </span>
                <h3 className="text-sm font-bold text-navy-950 dark:text-paper-100">
                  {previewReport.report_title}
                </h3>
              </div>
              <button
                onClick={() => setPreviewReport(null)}
                className="p-1 text-slate-400 hover:text-navy-950 dark:hover:text-paper-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="mt-4 space-y-4 text-xs font-sans">
              <div className="p-3.5 rounded-xl bg-paper-100 dark:bg-navy-950 border border-paper-300 dark:border-navy-800 font-mono space-y-1">
                <div className="flex justify-between">
                  <span className="text-slate-400">Claim Reference:</span>
                  <span className="font-bold">{previewReport.claim_number}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Carrier Loss Paid:</span>
                  <span>{formatCurrency(previewReport.paid_amount)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Net Recovery Target:</span>
                  <span className="font-bold text-teal-600 dark:text-teal-400">
                    {formatCurrency(previewReport.net_recovery_estimate)}
                  </span>
                </div>
              </div>

              <div>
                <h4 className="font-bold text-[11px] text-slate-400 mb-1">
                  Executive summary
                </h4>
                <p className="text-slate-700 dark:text-slate-300 leading-relaxed bg-paper-100 dark:bg-navy-950 p-3 rounded-xl border border-paper-200 dark:border-navy-800">
                  {previewReport.executive_summary}
                </p>
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  onClick={() => setPreviewReport(null)}
                  className="px-4 py-2 rounded-xl text-slate-400 hover:bg-paper-200 dark:hover:bg-navy-800"
                >
                  Close
                </button>
                <a
                  href={`/api/reports/${previewReport.report_id}/download`}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-brass-500 hover:bg-brass-600 text-navy-950 font-bold"
                >
                  <Download className="w-4 h-4" />
                  <span>Download PDF Document</span>
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
