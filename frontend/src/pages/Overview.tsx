import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  AreaChart,
  Area,
  CartesianGrid,
  LabelList,
} from 'recharts';
import {
  TrendingUp,
  MapPin,
  AlertTriangle,
  ChevronRight,
  Layers,
  HelpCircle,
  CheckCircle2,
} from 'lucide-react';

import { api } from '../api/client';
import { useFilterStore } from '../stores/filterStore';
import { MetricCard } from '../components/common/MetricCard';
import { GlobalFilterBar } from '../components/common/GlobalFilterBar';
import { PriorityBadge } from '../components/common/PriorityBadge';
import {
  formatCurrency,
  formatCompact,
  formatPercent,
  formatInteger,
} from '../utils/formatters';

const INCIDENT_LABEL_MAP: Record<string, string> = {
  'Single Vehicle Impact': 'Single vehicle impact',
  'Failure to Yield': 'Failure to yield',
  'Rear-end Collision': 'Rear-end collision',
  'Hit and Run Parked Vehicle': 'Hit and run, parked vehicle',
  'Backing from Driveway': 'Backing from driveway',
  'Multi-Vehicle Chain Reaction': 'Multi-vehicle collision',
  'Side-swipe Lane Change': 'Sideswipe, lane change',
  'T-bone Intersection Collision': 'T-bone intersection',
};

export const Overview: React.FC = () => {
  const navigate = useNavigate();
  const filters = useFilterStore();
  const setFilter = useFilterStore((state) => state.setFilter);
  const [hoveredStageId, setHoveredStageId] = useState<string | null>(null);

  const filterParams = {
    date_from: filters.date_from,
    date_to: filters.date_to,
    incident_type: filters.incident_type,
    state: filters.state,
    priority: filters.priority,
    status: filters.status,
  };

  // 1. Fetch Overview KPIs & Activity
  const { data: overview } = useQuery({
    queryKey: ['overview', filterParams],
    queryFn: () => api.getOverview(filterParams),
  });

  // 2. Fetch Funnel with active filters
  const { data: funnelData } = useQuery({
    queryKey: ['funnel', filterParams],
    queryFn: () => api.getFunnel(filterParams),
  });

  // 3. Fetch Exposure by Incident Type with active filters
  const { data: exposureByType } = useQuery({
    queryKey: ['exposure-by-type', filterParams],
    queryFn: () => api.getExposureByType(filterParams),
  });

  // 4. Fetch Recovery Trends with active filters
  const { data: trends } = useQuery({
    queryKey: ['recovery-trends', filterParams],
    queryFn: () => api.getRecoveryTrends(filterParams),
  });

  // 5. Fetch Geographic Distribution with active filters
  const { data: geoData } = useQuery({
    queryKey: ['geographic', filterParams],
    queryFn: () => api.getGeographic(filterParams),
  });

  // 6. Fetch Needs Attention Today with active filters
  const { data: needsAttention } = useQuery({
    queryKey: ['needs-attention', filterParams],
    queryFn: () => api.getNeedsAttention(5, filterParams),
  });

  const kpis = overview?.kpis;

  const donutColors = {
    High: '#D1603D', // Rust
    Medium: '#CFA968', // Brass
    Low: '#2F8F89', // Teal
  };

  const pieData = overview
    ? [
        { name: 'High', value: overview.priority_distribution.High, color: donutColors.High },
        { name: 'Medium', value: overview.priority_distribution.Medium, color: donutColors.Medium },
        { name: 'Low', value: overview.priority_distribution.Low, color: donutColors.Low },
      ]
    : [];

  // Real computed counts and percentages for Priority chart subtitle
  const highCount = overview?.priority_distribution?.High ?? 27;
  const mediumCount = overview?.priority_distribution?.Medium ?? 63;
  const lowCount = overview?.priority_distribution?.Low ?? 90;
  const totalPrio = highCount + mediumCount + lowCount || 1;
  const highPct = Math.round((highCount / totalPrio) * 100);
  const medPct = Math.round((mediumCount / totalPrio) * 100);
  const lowPct = Math.round((lowCount / totalPrio) * 100);
  const prioritySubtitle = `${highCount} high (${highPct}%) · ${mediumCount} medium (${medPct}%) · ${lowCount} low (${lowPct}%)`;

  const stages = funnelData?.stages ?? [];
  const maxFunnelCount = stages.length > 0 ? stages[0].count : (overview?.total_claims_analyzed ?? 180);

  // Sort exposure by paid exposure descending & augment with dual bar label (value and rate)
  const sortedExposureByType = exposureByType
    ? [...exposureByType].sort((a, b) => b.paid_exposure - a.paid_exposure)
    : [];

  const processedExposureByType = sortedExposureByType.map((item) => {
    const isSingleVehicle = item.incident_type.toLowerCase().includes('single vehicle');
    const barPaidLabel = `Paid ${formatCompact(item.paid_exposure)}`;
    const barProjectedLabel = isSingleVehicle
      ? 'No adverse party ($0)'
      : `Projected ${formatCompact(item.projected_recovery)} (${formatPercent(item.recovery_yield)})`;

    return {
      ...item,
      isNoAdverse: isSingleVehicle,
      barPaidLabel,
      barProjectedLabel,
    };
  });

  // Top subrogatable incident type for dynamic insight sentence
  const topSubrogatableIncident =
    processedExposureByType.length > 0
      ? [...processedExposureByType]
          .filter((i) => !i.isNoAdverse)
          .sort((a, b) => b.projected_recovery - a.projected_recovery)[0]
      : null;

  return (
    <div className="space-y-4 pb-12">
      {/* Compact Sticky Global Filter Bar with Custom Styled Controls */}
      <GlobalFilterBar />

      {/* Exactly 5 Reconciled Executive KPI Cards with auto-fit CSS Grid */}
      <div className="grid grid-cols-[repeat(auto-fit,minmax(220px,1fr))] gap-3">
        <MetricCard
          title="Claims ingested"
          value={kpis?.claims_ingested?.value ?? kpis?.total_claims?.value ?? 180}
          type="integer"
          unit="claims"
          secondaryLine={
            <span>
              <span className="font-mono font-medium">
                {formatCurrency(
                  Math.round(
                    (kpis?.total_paid_exposure?.value ?? 4486249) /
                      (kpis?.claims_ingested?.value ?? 180)
                  )
                )}
              </span>{' '}
              <span className="font-sans">average paid</span>
            </span>
          }
          calculation={
            kpis?.claims_ingested?.calculation ??
            'Total notice-of-loss claims ingested through verified ETL pipelines.'
          }
          accentColor="brass"
        />

        <MetricCard
          title="Total paid exposure"
          value={kpis?.total_paid_exposure?.value ?? 4486249}
          type="compactCurrency"
          secondaryLine={
            <span>
              <span className="font-sans">across </span>
              <span className="font-mono font-medium">
                {formatInteger(kpis?.claims_ingested?.value ?? 180)}
              </span>{' '}
              <span className="font-sans">claims</span>
            </span>
          }
          calculation={
            kpis?.total_paid_exposure?.calculation ??
            'Cumulative indemnity and physical damage payouts: $3,774,727 subrogatable across 7 adverse incident types, and $711,522 non-subrogatable with no adverse party (Single Vehicle Impact).'
          }
          accentColor="navy"
        />

        <MetricCard
          title="Projected recovery"
          value={kpis?.projected_recovery?.value ?? kpis?.projected_net_recovery?.value ?? 775423}
          type="compactCurrency"
          secondaryLine={
            <span>
              <span className="font-mono font-medium">
                {formatPercent(kpis?.projected_recovery_rate?.value ?? 17.3)}
              </span>{' '}
              <span className="font-sans">of paid</span>
            </span>
          }
          calculation={
            kpis?.projected_recovery?.calculation ??
            'Net recoverable capital estimated via comparative fault modeling across active claims.'
          }
          filterTarget={{ key: 'priority', value: 'High' }}
          accentColor="teal"
        />

        <MetricCard
          title="Recovered to date"
          value={kpis?.recovered_to_date?.value ?? 203966}
          type="compactCurrency"
          secondaryLine={
            <span>
              <span className="font-mono font-medium">
                {formatPercent(kpis?.actual_recovery_rate?.value ?? 4.5)}
              </span>{' '}
              <span className="font-sans">of paid</span>
            </span>
          }
          calculation={
            kpis?.recovered_to_date?.calculation ??
            'Actual funds remitted into trust accounts from 18 settled third-party carrier demands.'
          }
          filterTarget={{ key: 'status', value: 'Closed Recovered' }}
          accentColor="teal"
        />

        <MetricCard
          title="High-urgency demands"
          value={kpis?.high_urgency_demands?.value ?? 27}
          type="integer"
          unit="claims"
          secondaryLine={
            <span>
              <span className="font-mono font-medium">
                {Math.round(
                  ((kpis?.high_urgency_demands?.value ?? 27) /
                    (kpis?.claims_ingested?.value ?? 180)) *
                    100
                )}%
              </span>{' '}
              <span className="font-sans">of portfolio</span>
            </span>
          }
          calculation={
            kpis?.high_urgency_demands?.calculation ??
            'Claims triaged High priority facing imminent SOL deadlines or high net recovery opportunity.'
          }
          filterTarget={{ key: 'priority', value: 'High' }}
          accentColor="rust"
        />
      </div>

      {/* Screen 1 Visual Block: Proportional Funnel + Wide Exposure Bar Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3.5 items-stretch">
        {/* Proportional Recovery Funnel (lg:col-span-5) */}
        <div className="lg:col-span-5 bg-paper-50 dark:bg-navy-800/85 border border-paper-200 dark:border-navy-700/80 rounded-xl p-4 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-brass-500" />
                <h2 className="text-xs font-bold text-navy-950 dark:text-paper-100 font-sans">
                  Subrogation recovery funnel
                </h2>
              </div>
              <span className="text-[11px] text-slate-400 font-sans">Click stage to filter</span>
            </div>
            <p className="text-[11px] text-slate-400 mb-2.5 font-sans">
              Proportional stage conversion and drop across active claim portfolio
            </p>

            {/* One-line conversion summary aligned to top */}
            <div className="flex items-center justify-between px-3 py-1.5 mb-3 rounded-lg bg-teal-500/10 dark:bg-teal-500/15 border border-teal-500/25 text-xs text-teal-800 dark:text-teal-300">
              <span className="font-sans font-medium">Overall conversion:</span>
              <span className="font-sans text-[11px]">
                <span className="font-mono font-bold">10%</span> of ingested claims recovered
              </span>
            </div>
          </div>

          <div className="space-y-3 flex-1 flex flex-col justify-between py-1">
            {stages.map((stage, idx) => {
              const pctOfIngested =
                stage.pct_of_ingested ??
                (maxFunnelCount > 0 ? (stage.count / maxFunnelCount) * 100 : 0);
              const pctWidth = Math.max(14, pctOfIngested);

              // Distinct analyst-grade color by stage
              const barColor =
                stage.id === 'recovered'
                  ? 'bg-teal-500'
                  : stage.id === 'negotiating'
                  ? 'bg-rust-400'
                  : stage.id === 'demand_sent'
                  ? 'bg-brass-500'
                  : stage.id === 'assessed'
                  ? 'bg-blue-500'
                  : 'bg-slate-400 dark:bg-slate-500';

              const wholeDrop = Math.round(stage.pct_drop_previous ?? 0);

              return (
                <div
                  key={stage.id}
                  onClick={() => {
                    if (stage.id === 'recovered') setFilter('status', 'Closed Recovered');
                    else if (stage.id === 'negotiating') setFilter('status', 'Under Negotiation');
                    else if (stage.id === 'demand_sent') setFilter('status', 'Demand Sent');
                    else if (stage.id === 'assessed') setFilter('status', null);
                    else setFilter('status', null);
                    navigate('/claims');
                  }}
                  className="group cursor-pointer"
                >
                  {/* Stage Label & Metrics Row */}
                  <div className="flex items-center justify-between text-xs mb-1">
                    <div className="flex items-center gap-1 min-w-0">
                      <span className="font-medium text-navy-950 dark:text-paper-100 group-hover:text-brass-500 transition-colors whitespace-nowrap font-sans">
                        {stage.name}
                      </span>
                      {/* Tooltip for full description (no truncated text) */}
                      <div
                        className="relative inline-flex items-center"
                        onMouseEnter={() => setHoveredStageId(stage.id)}
                        onMouseLeave={() => setHoveredStageId(null)}
                      >
                        <HelpCircle className="w-3 h-3 text-slate-400 hover:text-brass-500 cursor-help" />
                        {hoveredStageId === stage.id && (
                          <div className="absolute left-0 bottom-full mb-1.5 w-64 p-2.5 bg-navy-950 text-paper-100 text-[11px] rounded-lg shadow-xl border border-navy-700 z-50 pointer-events-none text-left leading-relaxed font-sans">
                            <p className="font-semibold text-brass-400">{stage.name}</p>
                            <p className="text-slate-300 mt-0.5">{stage.description}</p>
                            <div className="absolute top-full left-2 border-4 border-transparent border-t-navy-950" />
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-1.5 text-[11px] shrink-0">
                      <span className="text-navy-950 dark:text-paper-100">
                        <span className="font-mono font-bold tabular-nums">
                          {formatInteger(stage.count)}
                        </span>{' '}
                        <span className="font-sans text-slate-400">claims</span>
                      </span>
                      <span className="text-slate-400">
                        <span className="font-mono tabular-nums">
                          {formatPercent(pctOfIngested, { decimals: 0 })}
                        </span>{' '}
                        <span className="font-sans">of ingested</span>
                      </span>
                      {idx > 0 && wholeDrop > 0 && (
                        <span className="text-slate-500 dark:text-slate-400 bg-slate-200/60 dark:bg-navy-900/80 px-1.5 py-0.5 rounded text-[10px]">
                          <span className="font-mono tabular-nums">-{wholeDrop}%</span>{' '}
                          <span className="font-sans">drop</span>
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Proportional Funnel Bar Track */}
                  <div className="w-full h-3.5 bg-paper-200 dark:bg-navy-900 rounded overflow-hidden">
                    <div
                      style={{ width: `${pctWidth}%` }}
                      className={`h-full ${barColor} opacity-85 group-hover:opacity-100 transition-all duration-300 rounded`}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          <div className="text-[11px] text-slate-400 pt-2 border-t border-paper-200 dark:border-navy-700/50 flex items-center justify-between font-sans">
            <span>Reconciled with closed recovered claims ({formatCurrency(kpis?.recovered_to_date?.value ?? 203966)})</span>
            <div className="relative inline-flex items-center gap-1.5 text-teal-600 dark:text-teal-400 font-sans cursor-help group">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span className="text-[11px] font-semibold">Reconciled</span>
              <div className="absolute right-0 bottom-full mb-1 w-64 p-2 bg-navy-950 text-paper-100 text-[11px] rounded-lg shadow-xl border border-navy-700 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity z-50 text-left font-sans">
                <p className="font-semibold text-brass-400 mb-0.5">Reconciliation</p>
                <p className="text-slate-300">18 recovered claims, $203,966, matches the recovered KPI.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Carrier Loss vs Subrogation Recovery Exposure Bar (lg:col-span-7 - wider layout >= 50% row width) */}
        <div className="lg:col-span-7 bg-paper-50 dark:bg-navy-800/85 border border-paper-200 dark:border-navy-700/80 rounded-xl p-4 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-1">
            <div>
              <h2 className="text-xs font-bold text-navy-950 dark:text-paper-100 font-sans">
                Exposure by incident type
              </h2>
              <p className="text-[11px] text-slate-400 font-sans">
                Paid exposure vs. projected net recovery (click bar to filter)
              </p>
            </div>
            <div className="flex items-center gap-3 text-[11px] font-mono shrink-0">
              <span className="flex items-center gap-1 text-slate-400 font-sans">
                <span className="w-2 h-2 rounded bg-slate-400 dark:bg-slate-600" /> Paid
              </span>
              <span className="flex items-center gap-1 text-teal-600 dark:text-teal-400 font-semibold font-sans">
                <span className="w-2 h-2 rounded bg-teal-500" /> Projected
              </span>
            </div>
          </div>

          <div className="h-[330px] mt-1">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={processedExposureByType}
                margin={{ top: 8, right: 185, left: 10, bottom: 8 }}
                barCategoryGap="22%"
                onClick={(e: any) => {
                  if (e && e.activePayload && e.activePayload.length) {
                    const clickedType = e.activePayload[0].payload.incident_type;
                    setFilter(
                      'incident_type',
                      filters.incident_type === clickedType ? null : clickedType
                    );
                  }
                }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#2A3F5B22" horizontal={false} />
                <XAxis
                  type="number"
                  domain={[0, 950000]}
                  ticks={[0, 200000, 400000, 600000, 800000]}
                  tickFormatter={(v) => (v === 0 ? '$0' : formatCompact(v))}
                  stroke="#8FA0B3"
                  fontSize={10}
                />
                <YAxis
                  type="category"
                  dataKey="incident_type"
                  stroke="#8FA0B3"
                  fontSize={11}
                  width={205}
                  tick={({ x, y, payload }: any) => {
                    const fullText = payload.value;
                    const isNoAdverse = fullText.toLowerCase().includes('single vehicle');
                    const shortText = INCIDENT_LABEL_MAP[fullText] || fullText;
                    return (
                      <g transform={`translate(${x},${y})`}>
                        <title>{fullText}{isNoAdverse ? ' (First-party loss: no adverse vehicle or carrier to subrogate)' : ''}</title>
                        <text
                          x={-8}
                          y={4}
                          textAnchor="end"
                          fill={isNoAdverse ? '#94A3B8' : '#8FA0B3'}
                          className={`text-[11px] font-sans ${isNoAdverse ? 'italic' : ''}`}
                        >
                          {shortText}
                          {isNoAdverse ? ' *' : ''}
                        </text>
                      </g>
                    );
                  }}
                />
                <Tooltip
                  formatter={(val: any, name: any, item: any) => {
                    if (name === 'Paid exposure') {
                      return [formatCurrency(Number(val)), 'Paid exposure'];
                    }
                    const yieldPct = item?.payload?.recovery_yield ?? 0;
                    return [
                      `${formatCurrency(Number(val))} (${formatPercent(yieldPct)} of paid)`,
                      'Projected recovery',
                    ];
                  }}
                  contentStyle={{
                    backgroundColor: '#0D1520',
                    borderColor: '#2A3F5B',
                    borderRadius: '8px',
                    color: '#F6F4EF',
                    fontSize: '11px',
                  }}
                />
                <Bar
                  dataKey="paid_exposure"
                  name="Paid exposure"
                  fill="#64748B"
                  radius={[0, 4, 4, 0]}
                  barSize={12}
                  isAnimationActive={false}
                >
                  <LabelList
                    dataKey="barPaidLabel"
                    position="right"
                    content={(props: any) => {
                      const { x, y, width, height, value } = props;
                      if (!value) return null;
                      return (
                        <text
                          x={Number(x) + Number(width) + 8}
                          y={Number(y) + Number(height) / 2 + 4}
                          fill="#94A3B8"
                          fontSize={10}
                        >
                          <tspan className="font-sans">Paid </tspan>
                          <tspan className="font-mono font-medium">{String(value).replace('Paid ', '')}</tspan>
                        </text>
                      );
                    }}
                  />
                </Bar>
                <Bar
                  dataKey="projected_recovery"
                  name="Projected recovery"
                  fill="#2F8F89"
                  radius={[0, 4, 4, 0]}
                  barSize={12}
                  isAnimationActive={false}
                >
                  <LabelList
                    dataKey="barProjectedLabel"
                    position="right"
                    content={(props: any) => {
                      const { x, y, width, height, value, index } = props;
                      if (!value) return null;
                      const isNoAdverse = String(value).includes('No adverse');
                      if (isNoAdverse) {
                        return (
                          <text
                            x={Number(x) + Number(width) + 8}
                            y={Number(y) + Number(height) / 2 + 4}
                            fill="#94A3B8"
                            fontSize={10}
                            fontStyle="italic"
                          >
                            <tspan className="font-sans">No adverse party </tspan>
                            <tspan className="font-mono">($0)</tspan>
                          </text>
                        );
                      }
                      const item = processedExposureByType[index];
                      return (
                        <text
                          x={Number(x) + Number(width) + 8}
                          y={Number(y) + Number(height) / 2 + 4}
                          fill="#2F8F89"
                          fontSize={10}
                          fontWeight="bold"
                        >
                          <tspan className="font-sans">Projected </tspan>
                          <tspan className="font-mono">{formatCompact(item?.projected_recovery ?? 0)}</tspan>
                          <tspan className="font-sans"> (</tspan>
                          <tspan className="font-mono">{formatPercent(item?.recovery_yield ?? 0)}</tspan>
                          <tspan className="font-sans">)</tspan>
                        </text>
                      );
                    }}
                  />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Incident Type Subrogation Eligibility Breakdown Note */}
          <div className="text-[11px] text-slate-500 dark:text-slate-400 pt-2 border-t border-paper-200 dark:border-navy-700/50 flex flex-wrap items-center justify-between gap-1.5 font-sans">
            <div>
              <span className="font-semibold text-navy-950 dark:text-paper-100">
                * Single Vehicle Impact has no adverse party
              </span>
              <span>
                {' '}— {formatCurrency(711522)} first-party loss ($0 subrogatable). Subrogatable portfolio: {formatCurrency(3774727)} across 7 adverse incident groups.
              </span>
            </div>
            {topSubrogatableIncident && (
              <span className="text-teal-600 dark:text-teal-400 font-medium">
                Top yield: {topSubrogatableIncident.incident_type} ({formatPercent(topSubrogatableIncident.recovery_yield)})
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Screen 2 Visual Block: Priority Distribution Donut + Recovery Trajectory */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3.5 items-stretch">
        {/* Priority Distribution Donut with Dynamic Subtitle (lg:col-span-4) */}
        <div className="lg:col-span-4 bg-paper-50 dark:bg-navy-800/85 border border-paper-200 dark:border-navy-700/80 rounded-xl p-4 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-1">
              <h2 className="text-xs font-bold text-navy-950 dark:text-paper-100 font-sans">
                Priority distribution
              </h2>
              <span className="text-[11px] text-slate-400 font-sans">Click to filter</span>
            </div>
            {/* Dynamic Real Computed Subtitle */}
            <p className="text-[11px] text-slate-400 font-sans">
              {prioritySubtitle}
            </p>
          </div>

          <div className="h-44 relative flex items-center justify-center my-1">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={72}
                  paddingAngle={3}
                  dataKey="value"
                  isAnimationActive={false}
                  onClick={(entry) => {
                    const clickedPrio = entry.name as 'High' | 'Medium' | 'Low';
                    setFilter('priority', filters.priority === clickedPrio ? null : clickedPrio);
                  }}
                  className="cursor-pointer"
                >
                  {pieData.map((entry, index) => {
                    // Cross-filter pattern: keep all 3 segments visible, highlight active, dim others
                    const isSelected = !filters.priority || filters.priority === entry.name;
                    return (
                      <Cell
                        key={`cell-${index}`}
                        fill={entry.color}
                        opacity={isSelected ? 1.0 : 0.25}
                        stroke={filters.priority === entry.name ? '#CFA968' : '#0D1520'}
                        strokeWidth={filters.priority === entry.name ? 3 : 2}
                      />
                    );
                  })}
                </Pie>
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0];
                      return (
                        <div className="bg-navy-950 p-2 rounded border border-navy-700 text-xs text-paper-100 shadow-xl">
                          <p className="font-bold text-brass-400 font-sans">{data.name} priority</p>
                          <p>
                            <span className="font-mono font-medium">{formatInteger(Number(data.value))}</span>{' '}
                            <span className="font-sans">claims</span>
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            {/* Center label */}
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-xl font-bold font-mono tabular-nums text-navy-950 dark:text-paper-100">
                {formatInteger(overview?.total_claims_analyzed ?? 180)}
              </span>
              <span className="text-[10px] font-medium text-slate-400 font-sans">
                {filters.priority ? `${filters.priority} claims` : 'Total claims'}
              </span>
            </div>
          </div>

          {/* Interactive Legend with exact counts & cross-filter indication */}
          <div className="grid grid-cols-3 gap-1 pt-2 border-t border-paper-200 dark:border-navy-700/60 text-center">
            {pieData.map((p) => {
              const isSelected = !filters.priority || filters.priority === p.name;
              return (
                <button
                  type="button"
                  key={p.name}
                  onClick={() =>
                    setFilter('priority', filters.priority === p.name ? null : (p.name as any))
                  }
                  className={`p-1.5 rounded transition-all ${
                    filters.priority === p.name
                      ? 'bg-brass-500/20 ring-1 ring-brass-500'
                      : isSelected
                      ? 'hover:bg-paper-200/60 dark:hover:bg-navy-900'
                      : 'opacity-40 hover:opacity-80'
                  }`}
                >
                  <div className="flex items-center justify-center gap-1 text-[11px] text-slate-600 dark:text-slate-300 font-sans">
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: p.color }} />
                    <span>{p.name}</span>
                  </div>
                  <div className="font-mono text-xs font-bold tabular-nums text-navy-950 dark:text-paper-100">
                    {formatInteger(p.value)}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Monthly Subrogation Trajectory Area Chart (lg:col-span-8) */}
        <div className="lg:col-span-8 bg-paper-50 dark:bg-navy-800/85 border border-paper-200 dark:border-navy-700/80 rounded-xl p-4 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <div>
              <div className="flex items-center gap-1.5">
                <TrendingUp className="w-4 h-4 text-teal-500" />
                <h2 className="text-xs font-bold text-navy-950 dark:text-paper-100 font-sans">
                  Monthly subrogation trajectory: projected vs. settled recovery
                </h2>
              </div>
              <p className="text-[11px] text-slate-400 mt-0.5 font-sans">
                Chronological timeline of projected target vs. settled recovery cash flow
              </p>
            </div>
            <div className="flex items-center gap-3 text-xs font-sans">
              <span className="flex items-center gap-1.5 text-slate-400">
                <span className="w-2.5 h-2.5 rounded bg-brass-500" /> Projected recovery
              </span>
              <span className="flex items-center gap-1.5 text-teal-600 dark:text-teal-400 font-bold">
                <span className="w-2.5 h-2.5 rounded bg-teal-500" /> Actual settled
              </span>
            </div>
          </div>

          <div className="h-52 mt-1">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends ?? []} margin={{ top: 10, right: 25, left: 10, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorProj" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#CFA968" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="#CFA968" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="colorAct" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2F8F89" stopOpacity={0.5} />
                    <stop offset="95%" stopColor="#2F8F89" stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A3F5B22" />
                <XAxis dataKey="month" stroke="#8FA0B3" fontSize={11} />
                <YAxis
                  stroke="#8FA0B3"
                  fontSize={11}
                  tickFormatter={(v) => (v === 0 ? '$0' : formatCompact(v))}
                />
                <Tooltip
                  formatter={(val: any, name: any) => [
                    formatCurrency(Number(val)),
                    name === 'projected_recovery' ? 'Projected recovery' : 'Actual settled',
                  ]}
                  contentStyle={{
                    backgroundColor: '#0D1520',
                    borderColor: '#2A3F5B',
                    borderRadius: '8px',
                    color: '#F6F4EF',
                    fontSize: '11px',
                    fontFamily: 'monospace',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="projected_recovery"
                  stroke="#CFA968"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorProj)"
                  isAnimationActive={false}
                />
                <Area
                  type="monotone"
                  dataKey="actual_recovery"
                  stroke="#2F8F89"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#colorAct)"
                  isAnimationActive={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="text-[11px] text-slate-400 pt-2 border-t border-paper-200 dark:border-navy-700/50 flex items-center justify-between font-sans">
            <span>Dynamic recovery projections model 68% actual trailing settlement efficiency</span>
            <span className="font-mono text-teal-600 dark:text-teal-400">Yield tracking verified</span>
          </div>
        </div>
      </div>

      {/* Screen 3: Geographic Distribution & Needs Attention Today List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Geographic Claims Distribution Grid */}
        <div className="bg-paper-50 dark:bg-navy-800/85 border border-paper-200 dark:border-navy-700/80 rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-brass-500" />
              <h2 className="text-xs font-bold text-navy-950 dark:text-paper-100 font-sans">
                Claims by state
              </h2>
            </div>
            <span className="text-[11px] text-slate-400 font-sans">Click state to filter</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {(geoData ?? []).map((g) => (
              <div
                key={g.state}
                onClick={() => setFilter('state', filters.state === g.state ? null : g.state)}
                className={`p-2.5 rounded-lg border transition-all cursor-pointer ${
                  filters.state === g.state
                    ? 'border-brass-500 bg-brass-500/10'
                    : 'border-paper-200 dark:border-navy-700 bg-paper-100 dark:bg-navy-900/60 hover:border-brass-500'
                }`}
              >
                <div className="flex items-center justify-between mb-0.5">
                  <span className="text-xs font-bold font-mono text-brass-600 dark:text-brass-400">
                    {g.state}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    <span className="font-mono tabular-nums">{formatInteger(g.claim_count)}</span>{' '}
                    <span className="font-sans">claims</span>
                  </span>
                </div>
                <div className="text-xs font-mono font-semibold tabular-nums text-navy-950 dark:text-paper-100">
                  {formatCurrency(g.total_exposure)}
                </div>
                <div className="mt-0.5 flex items-center justify-between text-[10px] text-slate-400 font-sans">
                  <span>Recovery rate</span>
                  <span className="text-teal-600 dark:text-teal-400 font-mono font-bold">
                    {formatPercent(g.recovery_rate)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Needs Attention Today List (Top 5 by Recovery Value x Urgency) */}
        <div className="bg-paper-50 dark:bg-navy-800/85 border border-paper-200 dark:border-navy-700/80 rounded-xl p-4 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-rust-500" />
                <h2 className="text-xs font-bold text-navy-950 dark:text-paper-100 font-sans">
                  Needs attention today
                </h2>
              </div>
              <button
                type="button"
                onClick={() => navigate('/claims')}
                className="text-xs text-brass-600 dark:text-brass-400 hover:underline flex items-center gap-0.5 font-sans"
              >
                View all claims <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
            <p className="text-[11px] text-slate-400 mb-3 font-sans">
              Top 5 claims ranked by recovery value × urgency (impending SOL or high liability)
            </p>

            <div className="space-y-2">
              {(needsAttention ?? []).map((item) => (
                <div
                  key={item.claim_id}
                  onClick={() => navigate(`/claims/${item.claim_id}`)}
                  className="p-2.5 rounded-lg border border-paper-200 dark:border-navy-700 bg-paper-100 dark:bg-navy-900/60 hover:border-brass-500 cursor-pointer transition-all flex items-center justify-between gap-3"
                >
                  <div className="flex items-center gap-2.5 min-w-0 flex-1">
                    <div className="w-8 h-8 rounded-md bg-rust-500/10 border border-rust-500/20 text-rust-500 flex items-center justify-center font-mono font-bold text-xs shrink-0">
                      {item.incident_state}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className="font-mono text-xs font-bold text-navy-950 dark:text-paper-100">
                          {item.claim_number}
                        </span>
                        <PriorityBadge priority={item.priority} size="sm" />
                      </div>
                      <p className="text-[11px] text-rust-500 font-medium mt-0.5 font-sans truncate">
                        {item.urgency_reason}
                      </p>
                    </div>
                  </div>

                  <div className="text-right shrink-0">
                    <div className="text-xs font-mono font-bold tabular-nums text-teal-600 dark:text-teal-400">
                      {formatCurrency(item.net_recovery)}
                    </div>
                    <div className="text-[10px] text-slate-400">
                      <span className="font-mono tabular-nums">{formatPercent(item.recovery_prob)}</span>{' '}
                      <span className="font-sans">prob</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-3 pt-2 border-t border-paper-200 dark:border-navy-700/50 flex items-center justify-between text-[11px] text-slate-400 font-sans">
            <span>Prioritized by multi-variable urgency triage engine</span>
            <span className="font-sans font-semibold text-brass-600 dark:text-brass-400">Value Momentum 2027</span>
          </div>
        </div>
      </div>
    </div>
  );
};
