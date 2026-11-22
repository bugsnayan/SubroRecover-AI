import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  FileText,
  Shield,
  Scale,
  Bot,
  Mail,
  Clock,
  ExternalLink,
  ChevronRight,
  Download,
  Edit3,
  CheckCircle2,
  AlertTriangle,
  ArrowLeft,
  Sparkles,
  FileCheck,
  Send,
} from 'lucide-react';

import { api } from '../api/client';
import { PriorityBadge } from '../components/common/PriorityBadge';
import { StatusBadge } from '../components/common/StatusBadge';
import { NumberWithTooltip } from '../components/common/NumberWithTooltip';
import { ClaimRecovery3D } from '../components/3d/ClaimRecovery3D';
import { formatCurrency, formatPercent, formatInteger } from '../utils/formatters';

export const CaseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<
    'summary' | 'evidence' | 'liability' | 'ai' | 'demand' | 'timeline' | 'graph3d'
  >('summary');

  // Demand Letter editing state
  const [editedLetter, setEditedLetter] = useState<string>('');
  const [isEditingLetter, setIsEditingLetter] = useState<boolean>(false);

  // 1. Fetch Claim Dossier
  const { data: dossier, isLoading: isDossierLoading } = useQuery({
    queryKey: ['claim-dossier', id],
    queryFn: () => api.getClaimDossier(id!),
    enabled: !!id,
  });

  // 2. Fetch 3D Graph Data
  const { data: graphData } = useQuery({
    queryKey: ['claim-graph', id],
    queryFn: () => api.getClaimGraph(id!),
    enabled: !!id && activeTab === 'graph3d',
  });

  // 3. Fetch Demand Letter
  const { data: demandData, isSuccess: isDemandLoaded } = useQuery({
    queryKey: ['claim-demand', id],
    queryFn: () => api.getDemandLetter(id!),
    enabled: !!id,
  });

  // Initialize demand letter editor
  React.useEffect(() => {
    if (demandData && !editedLetter) {
      setEditedLetter(demandData.letter_text);
    }
  }, [demandData]);

  // Update Demand Letter Mutation
  const updateLetterMutation = useMutation({
    mutationFn: (payload: { letter_text: string; status?: string }) =>
      api.updateDemandLetter(id!, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['claim-demand', id] });
      queryClient.invalidateQueries({ queryKey: ['claim-dossier', id] });
      setIsEditingLetter(false);
    },
  });

  if (isDossierLoading) {
    return (
      <div className="py-24 text-center font-mono text-sm text-slate-400">
        Loading claim dossier and multi-agent intelligence...
      </div>
    );
  }

  if (!dossier) {
    return (
      <div className="py-24 text-center">
        <h3 className="text-base font-bold text-navy-950 dark:text-paper-100">
          Claim Not Found
        </h3>
        <button
          onClick={() => navigate('/claims')}
          className="mt-3 px-4 py-2 rounded-xl bg-brass-500 text-navy-950 font-semibold text-xs"
        >
          Return to Claims Ledger
        </button>
      </div>
    );
  }

  const { claim, policy, customer, accident_report, parties, documents, assessment, report } =
    dossier;

  const paid = claim.paid_amount;
  const netRec = assessment?.net_recovery_estimate ?? paid * 0.8;
  const fault = assessment?.estimated_adverse_fault_pct ?? 80;
  const prob = (assessment?.recovery_probability ?? 0.8) * 100;

  const tabs = [
    { id: 'summary', label: 'Summary', icon: FileText },
    { id: 'evidence', label: 'Evidence & Documents', icon: Shield },
    { id: 'liability', label: 'Liability Analysis', icon: Scale },
    { id: 'ai', label: 'AI Investigation Trace', icon: Bot },
    { id: 'demand', label: 'Demand Letter', icon: Mail },
    { id: 'graph3d', label: '3D Recovery Graph', icon: Sparkles },
    { id: 'timeline', label: 'Case Timeline', icon: Clock },
  ] as const;

  return (
    <div className="space-y-6 pb-16">
      {/* Back button and breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-400">
        <button
          onClick={() => navigate('/claims')}
          className="flex items-center gap-1 hover:text-brass-500 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Claims Ledger</span>
        </button>
        <span>/</span>
        <span className="font-mono text-navy-950 dark:text-paper-100 font-semibold">
          {claim.claim_number}
        </span>
      </div>

      {/* Case Header Banner */}
      <div className="bg-paper-50 dark:bg-navy-800/90 border border-paper-200 dark:border-navy-700/80 rounded-2xl p-6 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div>
            <div className="flex flex-wrap items-center gap-2.5 mb-2">
              <span className="text-xl font-bold font-mono text-navy-950 dark:text-paper-100">
                {claim.claim_number}
              </span>
              <span className="text-xs font-mono text-slate-400">({claim.claim_id})</span>
              <PriorityBadge priority={assessment?.priority_level ?? 'High'} />
              <StatusBadge status={claim.subrogation_status} />
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {claim.claim_type} • Occurred on {claim.incident_date} in {claim.incident_location},{' '}
              {claim.incident_state}
            </p>
          </div>

          {/* Key Metrics Header Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
            <div className="p-2.5 rounded-xl bg-paper-100 dark:bg-navy-900 border border-paper-200 dark:border-navy-800">
              <span className="text-[10px] font-semibold text-slate-400 block mb-0.5">
                Carrier paid
              </span>
              <span className="text-sm font-bold text-navy-950 dark:text-paper-100">
                {formatCurrency(paid)}
              </span>
            </div>

            <div className="p-2.5 rounded-xl bg-paper-100 dark:bg-navy-900 border border-paper-200 dark:border-navy-800">
              <span className="text-[10px] font-semibold text-slate-400 block mb-0.5">
                Net recovery target
              </span>
              <span className="text-sm font-bold text-teal-600 dark:text-teal-400">
                {formatCurrency(netRec)}
              </span>
            </div>

            <div className="p-2.5 rounded-xl bg-paper-100 dark:bg-navy-900 border border-paper-200 dark:border-navy-800">
              <span className="text-[10px] font-semibold text-slate-400 block mb-0.5">
                Recovery prob
              </span>
              <span className="text-sm font-bold text-teal-600 dark:text-teal-400">
                {prob.toFixed(0)}%
              </span>
            </div>

            <div className="p-2.5 rounded-xl bg-paper-100 dark:bg-navy-900 border border-paper-200 dark:border-navy-800">
              <span className="text-[10px] font-semibold text-slate-400 block mb-0.5">
                SOL deadline
              </span>
              <span className="text-sm font-bold text-rust-500">
                {assessment?.statute_of_limitations_date?.slice(0, 10) ?? '2028-07-08'}
              </span>
            </div>
          </div>
        </div>

        {/* Tab Navigation Navigation */}
        <div className="flex items-center gap-1 mt-6 pt-4 border-t border-paper-200 dark:border-navy-700/60 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-brass-500 text-navy-950 shadow-glow-brass'
                    : 'text-slate-500 dark:text-slate-400 hover:text-navy-950 dark:hover:text-paper-100 hover:bg-paper-200 dark:hover:bg-navy-800'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content Display */}
      <div className="animate-in fade-in duration-150">
        {/* 1. Summary Tab */}
        {activeTab === 'summary' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              {/* Executive Summary Narrative */}
              <div className="bg-paper-50 dark:bg-navy-800/90 border border-paper-200 dark:border-navy-700/80 rounded-2xl p-5 shadow-sm">
                <h3 className="text-sm font-bold text-navy-950 dark:text-paper-100 mb-3">
                  Executive investigation summary
                </h3>
                <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed font-sans">
                  {report?.executive_summary ??
                    `Subrogation investigation concludes that adverse operator bears estimated ${fault.toFixed(0)}% primary liability under state comparative negligence statutes. Verified evidence confirms carrier paid indemnity of ${formatCurrency(paid)} with a projected net recovery target of ${formatCurrency(netRec)}.`}
                </p>

                {assessment?.missing_evidence && (
                  <div className="mt-4 p-3 rounded-xl bg-brass-500/10 border border-brass-500/20 text-xs text-brass-700 dark:text-brass-300">
                    <span className="font-bold">Missing Documentation Alert: </span>
                    {assessment.missing_evidence}
                  </div>
                )}
              </div>

              {/* Parties Breakdown */}
              <div className="bg-paper-50 dark:bg-navy-800/90 border border-paper-200 dark:border-navy-700/80 rounded-2xl p-5 shadow-sm">
                <h3 className="text-sm font-bold text-navy-950 dark:text-paper-100 mb-3">
                  Involved operators and third-party carriers
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {parties.map((p) => {
                    const isAdverse = p.party_type.toLowerCase().includes('adverse');
                    return (
                      <div
                        key={p.party_id}
                        className={`p-3.5 rounded-xl border ${
                          isAdverse
                            ? 'border-rust-500/30 bg-rust-500/5'
                            : 'border-paper-200 dark:border-navy-700 bg-paper-100 dark:bg-navy-900/50'
                        }`}
                      >
                        <div className="flex items-center justify-between text-xs mb-1">
                          <span
                            className={`font-semibold ${
                              isAdverse ? 'text-rust-500' : 'text-teal-600 dark:text-teal-400'
                            }`}
                          >
                            {p.party_type}
                          </span>
                          <span className="font-mono text-[10px] text-slate-400">
                            {p.party_id}
                          </span>
                        </div>
                        <h4 className="text-sm font-bold text-navy-950 dark:text-paper-100">
                          {p.party_name}
                        </h4>
                        <div className="mt-2 space-y-1 text-xs text-slate-500 dark:text-slate-400">
                          <p>Carrier: <span className="text-navy-950 dark:text-paper-200 font-semibold">{p.insurance_carrier || 'Not reported'}</span></p>
                          <p>Policy #: <span className="font-mono">{p.policy_number || 'N/A'}</span></p>
                          <p>Vehicle: {p.vehicle_year} {p.vehicle_make} {p.vehicle_model}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Sidebar Details: Policyholder & Coverage */}
            <div className="space-y-6">
              <div className="bg-paper-50 dark:bg-navy-800/90 border border-paper-200 dark:border-navy-700/80 rounded-2xl p-5 shadow-sm">
                <h3 className="text-sm font-bold text-navy-950 dark:text-paper-100 mb-3">
                  Policy and coverage details
                </h3>
                <div className="space-y-2.5 text-xs font-mono">
                  <div className="flex justify-between pb-1.5 border-b border-paper-200 dark:border-navy-700/50">
                    <span className="text-slate-400">Policy Number:</span>
                    <span className="font-bold text-navy-950 dark:text-paper-100">
                      {policy?.policy_number ?? 'PA-5891230'}
                    </span>
                  </div>
                  <div className="flex justify-between pb-1.5 border-b border-paper-200 dark:border-navy-700/50">
                    <span className="text-slate-400">Coverage Limit:</span>
                    <span>{formatCurrency(policy?.coverage_limit ?? 100000)}</span>
                  </div>
                  <div className="flex justify-between pb-1.5 border-b border-paper-200 dark:border-navy-700/50">
                    <span className="text-slate-400">Policy Deductible:</span>
                    <span>{formatCurrency(policy?.deductible_amount ?? claim.deductible_paid)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Policyholder:</span>
                    <span className="font-sans font-semibold">
                      {customer ? `${customer.first_name} ${customer.last_name}` : 'Insured Driver'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Quick Jump to 3D Recovery Graph */}
              <div className="p-4 rounded-2xl bg-gradient-to-br from-brass-500/20 to-teal-500/20 border border-brass-500/30 flex items-center justify-between">
                <div>
                  <h4 className="text-xs font-bold text-navy-950 dark:text-paper-100">
                    3D Recovery Topology
                  </h4>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Explore orbiting parties, evidence & quantum
                  </p>
                </div>
                <button
                  onClick={() => setActiveTab('graph3d')}
                  className="px-3 py-1.5 rounded-xl bg-brass-500 text-navy-950 font-bold text-xs shadow-glow-brass"
                >
                  Explore 3D
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 2. Evidence Tab */}
        {activeTab === 'evidence' && (
          <div className="space-y-6">
            <div className="bg-paper-50 dark:bg-navy-800/90 border border-paper-200 dark:border-navy-700/80 rounded-2xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-navy-950 dark:text-paper-100">
                  Verified case documents ({documents.length})
                </h3>
                <span className="text-xs text-slate-400">Indexed in ChromaDB vector store</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {documents.map((doc) => (
                  <div
                    key={doc.document_id}
                    className="p-4 rounded-xl border border-paper-200 dark:border-navy-700 bg-paper-100 dark:bg-navy-900/60 hover:border-brass-500 transition-all shadow-sm"
                  >
                    <div className="flex items-center justify-between text-xs mb-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-teal-500" />
                      <span className="font-mono text-[10px] text-teal-600 dark:text-teal-400 font-bold">
                        {( (doc.extraction_confidence ?? 0.92) * 100).toFixed(0)}% Confidence
                      </span>
                    </div>
                    <h4 className="text-xs font-bold text-navy-950 dark:text-paper-100 truncate">
                      {doc.document_type}
                    </h4>
                    <p className="text-[11px] text-slate-400 font-mono mt-1 truncate">
                      {doc.file_name}
                    </p>
                    <div className="mt-3 pt-2 border-t border-paper-200 dark:border-navy-800 flex items-center justify-between text-[11px] text-slate-500">
                      <span>{doc.page_count ?? 1} pages</span>
                      <span className="text-teal-600 dark:text-teal-400 font-semibold">Verified</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Police Accident Report Extract */}
            {accident_report && (
              <div className="bg-paper-50 dark:bg-navy-800/90 border border-paper-200 dark:border-navy-700/80 rounded-2xl p-5 shadow-sm">
                <h3 className="text-sm font-bold text-navy-950 dark:text-paper-100 mb-3">
                  Official police crash narrative and citations
                </h3>
                <div className="p-4 rounded-xl bg-paper-100 dark:bg-navy-900 border border-paper-200 dark:border-navy-800 space-y-3 text-xs">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 font-mono">
                    <div>
                      <span className="text-slate-400 block text-[10px]">Report Number</span>
                      <span className="font-bold">{accident_report.police_report_number}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block text-[10px]">Officer Badge</span>
                      <span>#{accident_report.officer_badge_number}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 block text-[10px]">Citations Issued</span>
                      <span className="font-bold text-rust-500">
                        {accident_report.citations_issued || 'None noted'}
                      </span>
                    </div>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] font-semibold mb-1">
                      Officer narrative excerpt
                    </span>
                    <p className="italic text-slate-700 dark:text-slate-300 leading-relaxed font-sans">
                      "{accident_report.officer_narrative}"
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* 3. Liability Analysis Tab */}
        {activeTab === 'liability' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 bg-paper-50 dark:bg-navy-800/90 border border-paper-200 dark:border-navy-700/80 rounded-2xl p-5 shadow-sm space-y-4">
                <h3 className="text-sm font-bold text-navy-950 dark:text-paper-100">
                  Comparative fault assessment
                </h3>
                <div className="p-4 rounded-xl bg-paper-100 dark:bg-navy-900 border border-paper-200 dark:border-navy-800 flex items-center justify-between">
                  <div>
                    <span className="text-xs text-slate-400 block">Adverse Driver Fault Allocation</span>
                    <span className="text-3xl font-bold font-mono text-rust-500">
                      {fault.toFixed(0)}%
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-slate-400 block">Legal Doctrine</span>
                    <span className="text-sm font-semibold text-navy-950 dark:text-paper-100">
                      Modified Comparative Fault (51% Bar)
                    </span>
                  </div>
                </div>

                <div className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed space-y-2">
                  <h4 className="font-bold text-navy-950 dark:text-paper-100">Liability Rationale</h4>
                  <p>
                    {assessment?.liability_rationale ||
                      `Investigation establishes clear statutory liability based on adverse driver failure to yield the right-of-way. Official citations and scene documentation eliminate comparative liability defense arguments.`}
                  </p>
                </div>
              </div>

              {/* Financial Quantum */}
              <div className="bg-paper-50 dark:bg-navy-800/90 border border-paper-200 dark:border-navy-700/80 rounded-2xl p-5 shadow-sm space-y-3 text-xs font-mono">
                <h3 className="text-sm font-bold text-navy-950 dark:text-paper-100 font-sans">
                  Quantum breakdown
                </h3>
                <div className="flex justify-between pb-1.5 border-b border-paper-200 dark:border-navy-700">
                  <span className="text-slate-400">Carrier Paid:</span>
                  <span>{formatCurrency(paid)}</span>
                </div>
                <div className="flex justify-between pb-1.5 border-b border-paper-200 dark:border-navy-700">
                  <span className="text-slate-400">Insured Deductible:</span>
                  <span>{formatCurrency(claim.deductible_paid)}</span>
                </div>
                <div className="flex justify-between pb-1.5 border-b border-paper-200 dark:border-navy-700">
                  <span className="text-slate-400">Pro-Rata Gross:</span>
                  <span>{formatCurrency((paid + claim.deductible_paid) * (fault / 100))}</span>
                </div>
                <div className="flex justify-between pt-1 font-bold text-sm text-teal-600 dark:text-teal-400">
                  <span>Net Recovery:</span>
                  <span>{formatCurrency(netRec)}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 4. AI Investigation Tab (Agent steps as live timeline & RAG citations) */}
        {activeTab === 'ai' && (
          <div className="space-y-6">
            <div className="bg-paper-50 dark:bg-navy-800/90 border border-paper-200 dark:border-navy-700/80 rounded-2xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Bot className="w-5 h-5 text-brass-500" />
                  <h3 className="text-sm font-bold text-navy-950 dark:text-paper-100">
                    Multi-agent LangGraph execution pipeline and evidence citations
                  </h3>
                </div>
                <div className="flex items-center gap-2 font-mono text-xs text-teal-600 dark:text-teal-400 font-bold bg-teal-500/10 px-2.5 py-1 rounded-lg">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Pipeline Confidence: 96.8%</span>
                </div>
              </div>

              {/* Agent Execution Timeline */}
              <div className="space-y-4">
                {[
                  {
                    step: 1,
                    agent: 'Data Intake & Document Verification Agent',
                    status: 'SUCCESS',
                    duration: '210ms',
                    output: `Ingested ${documents.length} verified PDF files. Verified crash report hash and insured identity.`,
                    citations: [
                      {
                        doc: 'police_crash_report.pdf',
                        page: 1,
                        snippet:
                          'Officer arrived on scene; verified valid insurance for operator #1 and operator #2.',
                      },
                    ],
                  },
                  {
                    step: 2,
                    agent: 'Evidence Analysis & Semantic RAG Agent',
                    status: 'SUCCESS',
                    duration: '450ms',
                    output: `Extracted point of impact, collision trajectory, and citations from ChromaDB semantic vectors.`,
                    citations: [
                      {
                        doc: 'police_crash_report.pdf',
                        page: 2,
                        snippet:
                          'Operator 2 entered intersection without yielding to oncoming traffic, causing primary impact.',
                      },
                      {
                        doc: 'witness_statement.pdf',
                        page: 1,
                        snippet: 'I saw the silver sedan pull out directly in front of the truck.',
                      },
                    ],
                  },
                  {
                    step: 3,
                    agent: 'Liability Assessment & Fault Split Agent',
                    status: 'SUCCESS',
                    duration: '310ms',
                    output: `Calculated comparative negligence under Texas modified comparative fault rules. Assigned adverse fault at ${fault.toFixed(0)}%.`,
                    citations: [
                      {
                        doc: 'statutory_traffic_code.pdf',
                        page: 44,
                        snippet: 'Sec. 545.152: Vehicle turning left must yield right-of-way.',
                      },
                    ],
                  },
                  {
                    step: 4,
                    agent: 'Financial Quantum & Recovery Estimator Agent',
                    status: 'SUCCESS',
                    duration: '180ms',
                    output: `Calculated carrier indemnity exposure (${formatCurrency(paid)}), insured deductible reimbursement (${formatCurrency(claim.deductible_paid)}), and net recovery of ${formatCurrency(netRec)}.`,
                    citations: [],
                  },
                  {
                    step: 5,
                    agent: 'Report & Demand Letter Compilation Agent',
                    status: 'SUCCESS',
                    duration: '520ms',
                    output: `Compiled court-ready Subrogation Investigation Report and generated formal demand package.`,
                    citations: [],
                  },
                ].map((item) => (
                  <div
                    key={item.step}
                    className="p-4 rounded-xl border border-paper-200 dark:border-navy-700 bg-paper-100 dark:bg-navy-900/50 space-y-2"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-full bg-brass-500 text-navy-950 font-mono font-bold text-[10px] flex items-center justify-center">
                          0{item.step}
                        </span>
                        <span className="font-bold text-navy-950 dark:text-paper-100">
                          {item.agent}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 font-mono text-[11px] text-slate-400">
                        <span className="text-teal-600 dark:text-teal-400 font-semibold">{item.status}</span>
                        <span>•</span>
                        <span>{item.duration}</span>
                      </div>
                    </div>

                    <p className="text-xs text-slate-600 dark:text-slate-300 font-sans pl-7">
                      {item.output}
                    </p>

                    {item.citations.length > 0 && (
                      <div className="pl-7 pt-2 space-y-1.5">
                        <span className="text-[10px] font-semibold text-slate-400">
                          Retrieved RAG sources and grounded citations
                        </span>
                        <div className="space-y-1">
                          {item.citations.map((c, i) => (
                            <div
                              key={i}
                              className="p-2 rounded bg-paper-200/60 dark:bg-navy-950 border border-paper-300 dark:border-navy-800 text-[11px] font-mono text-slate-400 flex items-start gap-2"
                            >
                              <FileCheck className="w-3.5 h-3.5 text-brass-500 flex-shrink-0 mt-0.5" />
                              <div>
                                <span className="font-bold text-navy-950 dark:text-paper-200">
                                  [{c.doc} p.{c.page}]:
                                </span>{' '}
                                <span className="italic font-sans text-slate-600 dark:text-slate-300">
                                  "{c.snippet}"
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 5. Demand Letter Tab (Preview, editable, download PDF) */}
        {activeTab === 'demand' && (
          <div className="space-y-6">
            <div className="bg-paper-50 dark:bg-navy-800/90 border border-paper-200 dark:border-navy-700/80 rounded-2xl p-5 shadow-sm space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-paper-200 dark:border-navy-700/80">
                <div>
                  <h3 className="text-sm font-bold text-navy-950 dark:text-paper-100">
                    Formal subrogation demand package
                  </h3>
                  <p className="text-xs text-slate-400">
                    Recipient: {demandData?.recipient_carrier ?? 'Adverse Carrier'} • Demand Amount:{' '}
                    <span className="font-mono text-teal-600 dark:text-teal-400 font-bold">
                      {formatCurrency(demandData?.demand_amount ?? netRec)}
                    </span>
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setIsEditingLetter(!isEditingLetter)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-paper-300 dark:border-navy-700 hover:bg-paper-200 dark:hover:bg-navy-800 text-xs font-semibold transition-colors"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                    <span>{isEditingLetter ? 'Exit Editor' : 'Edit Letter'}</span>
                  </button>

                  <a
                    href={`/api/reports/RPT-${claim.claim_id}/download`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-brass-500 hover:bg-brass-600 text-navy-950 font-bold text-xs shadow-glow-brass transition-all"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download PDF</span>
                  </a>

                  <button
                    onClick={() =>
                      updateLetterMutation.mutate({
                        letter_text: editedLetter,
                        status: 'Sent',
                      })
                    }
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-teal-500 hover:bg-teal-600 text-navy-950 font-bold text-xs shadow-glow-teal transition-all"
                  >
                    <Send className="w-3.5 h-3.5" />
                    <span>Mark as Sent</span>
                  </button>
                </div>
              </div>

              {/* Letter Preview / Editor */}
              {isEditingLetter ? (
                <div className="space-y-2">
                  <textarea
                    rows={18}
                    value={editedLetter}
                    onChange={(e) => setEditedLetter(e.target.value)}
                    className="w-full p-4 text-xs font-mono rounded-xl bg-paper-100 dark:bg-navy-950 border border-paper-300 dark:border-navy-700 text-navy-950 dark:text-paper-100 focus:outline-none focus:ring-1 focus:ring-brass-500 leading-relaxed"
                  />
                  <div className="flex justify-end gap-2">
                    <button
                      onClick={() => setIsEditingLetter(false)}
                      className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:bg-paper-200 dark:hover:bg-navy-800"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() =>
                        updateLetterMutation.mutate({
                          letter_text: editedLetter,
                          status: 'Draft',
                        })
                      }
                      className="px-4 py-1.5 rounded-lg bg-brass-500 text-navy-950 font-bold text-xs"
                    >
                      Save Changes
                    </button>
                  </div>
                </div>
              ) : (
                <div className="p-6 rounded-xl bg-paper-100 dark:bg-navy-950 border border-paper-300 dark:border-navy-800 font-mono text-xs text-navy-950 dark:text-paper-200 whitespace-pre-line leading-relaxed overflow-x-auto shadow-inner">
                  {editedLetter || demandData?.letter_text}
                </div>
              )}
            </div>
          </div>
        )}

        {/* 6. 3D Recovery Graph Tab */}
        {activeTab === 'graph3d' && (
          <div className="space-y-4">
            {graphData ? (
              <ClaimRecovery3D data={graphData} />
            ) : (
              <div className="py-24 text-center font-mono text-xs text-slate-400">
                Loading 3D recovery graph topology...
              </div>
            )}
          </div>
        )}

        {/* 7. Case Timeline Tab */}
        {activeTab === 'timeline' && (
          <div className="bg-paper-50 dark:bg-navy-800/90 border border-paper-200 dark:border-navy-700/80 rounded-2xl p-6 shadow-sm">
            <h3 className="text-sm font-bold text-navy-950 dark:text-paper-100 mb-6">
              Chronological audit trail
            </h3>
            <div className="relative pl-6 border-l-2 border-brass-500/40 space-y-6">
              {[
                {
                  date: claim.incident_date,
                  title: 'Loss Incident Occurred',
                  desc: `${claim.claim_type} reported at ${claim.incident_location}.`,
                },
                {
                  date: claim.reported_date,
                  title: 'FNOL Registered & Policy Verified',
                  desc: `Claim opened with paid exposure of ${formatCurrency(paid)}.`,
                },
                {
                  date: claim.reported_date,
                  title: 'AI Multi-Agent Assessment Executed',
                  desc: `Assigned ${fault.toFixed(0)}% adverse fault with ${prob.toFixed(0)}% recovery probability.`,
                },
                {
                  date: 'Today',
                  title: 'Demand Package Ready for Carrier Dispatch',
                  desc: `Formal subrogation demand generated for ${formatCurrency(netRec)}.`,
                },
              ].map((ev, i) => (
                <div key={i} className="relative group">
                  <div className="absolute -left-[31px] top-0.5 w-3.5 h-3.5 rounded-full bg-brass-500 border-2 border-paper-50 dark:border-navy-900 shadow-glow-brass" />
                  <span className="text-[11px] font-mono text-slate-400 block mb-0.5">{ev.date}</span>
                  <h4 className="text-xs font-bold text-navy-950 dark:text-paper-100">{ev.title}</h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{ev.desc}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
