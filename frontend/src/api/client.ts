import {
  Claim,
  ClaimDossier,
  RecoveryGraphData,
  PortfolioResponse,
  OverviewData,
  FunnelStage,
  ExposureByTypeItem,
  RecoveryTrendItem,
  GeographicItem,
  NeedsAttentionItem,
  ChatResponse,
  ReportItem,
  ModelMetrics,
} from '../types';

const BASE_URL = '';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const errorBody = await res.text().catch(() => '');
    throw new Error(`API Error ${res.status}: ${res.statusText} — ${errorBody}`);
  }
  return res.json();
}

function toQueryString(paramsObj?: Record<string, any>): string {
  if (!paramsObj) return '';
  const params = new URLSearchParams();
  Object.entries(paramsObj).forEach(([k, v]) => {
    if (v !== null && v !== undefined && v !== '') {
      params.append(k, String(v));
    }
  });
  const qs = params.toString();
  return qs ? `?${qs}` : '';
}

export const api = {
  // System Health
  getHealth: () => fetchJson<{ status: string; database_connected: boolean; environment: string }>('/api/health'),

  // Analytics Overview (supports query params from FilterStore)
  getOverview: (filters?: Record<string, string | null>) =>
    fetchJson<OverviewData>(`/api/analytics/overview${toQueryString(filters)}`),

  getFunnel: (filters?: Record<string, string | null>) =>
    fetchJson<{ stages: FunnelStage[] }>(`/api/analytics/funnel${toQueryString(filters)}`),

  getExposureByType: (filters?: Record<string, string | null>) =>
    fetchJson<ExposureByTypeItem[]>(`/api/analytics/exposure-by-type${toQueryString(filters)}`),

  getRecoveryTrends: (filters?: Record<string, string | null>) =>
    fetchJson<RecoveryTrendItem[]>(`/api/analytics/recovery-trends${toQueryString(filters)}`),

  getGeographic: (filters?: Record<string, string | null>) =>
    fetchJson<GeographicItem[]>(`/api/analytics/geographic${toQueryString(filters)}`),

  getNeedsAttention: (limit: number = 5, filters?: Record<string, string | null>) =>
    fetchJson<NeedsAttentionItem[]>(`/api/analytics/needs-attention${toQueryString({ limit, ...filters })}`),

  // Claims
  getClaims: (paramsObj?: Record<string, any>) => {
    const params = new URLSearchParams();
    if (paramsObj) {
      Object.entries(paramsObj).forEach(([k, v]) => {
        if (v !== null && v !== undefined && v !== '') {
          params.append(k, String(v));
        }
      });
    }
    const query = params.toString() ? `?${params.toString()}` : '';
    return fetchJson<Claim[]>(`/api/claims${query}`);
  },

  getClaimDossier: (claimId: string) => fetchJson<ClaimDossier>(`/api/claims/${claimId}`),

  getPortfolio3D: () => fetchJson<PortfolioResponse>('/api/claims/portfolio-3d'),

  getClaimGraph: (claimId: string) => fetchJson<RecoveryGraphData>(`/api/claims/${claimId}/graph`),

  getDemandLetter: (claimId: string) =>
    fetchJson<{
      claim_id: string;
      claim_number: string;
      recipient_carrier: string;
      demand_amount: number;
      letter_text: string;
      status: string;
      fault_pct: number;
      sol_date: string;
    }>(`/api/claims/${claimId}/demand-letter`),

  updateDemandLetter: (
    claimId: string,
    payload: { letter_text: string; status?: string; demand_amount?: number }
  ) =>
    fetchJson<{ claim_id: string; status: string; message: string; letter_text: string }>(
      `/api/claims/${claimId}/demand-letter`,
      {
        method: 'PUT',
        body: JSON.stringify(payload),
      }
    ),

  // AI Assistant Chat
  sendChatMessage: (query: string, claimId?: string) =>
    fetchJson<ChatResponse>('/api/assistant/chat', {
      method: 'POST',
      body: JSON.stringify({ query, claim_id: claimId }),
    }),

  // Reports
  getReports: (limit: number = 50) => fetchJson<ReportItem[]>(`/api/reports?limit=${limit}`),

  getReportDetail: (reportId: string) => fetchJson<any>(`/api/reports/${reportId}`),

  generateReport: (payload: { claim_id: string; scope?: string; notes?: string }) =>
    fetchJson<{
      message: string;
      report_id: string;
      report_number: string;
      claim_id: string;
      download_url: string;
      dossier: any;
    }>('/api/reports/generate', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // Data Quality & Model
  getPipelineStatus: () =>
    fetchJson<{
      latest_execution: any;
      run_history: any[];
    }>('/api/pipeline/status'),

  triggerPipelineRun: () =>
    fetchJson<any>('/api/pipeline/run', {
      method: 'POST',
    }),

  getModelMetrics: () => fetchJson<ModelMetrics>('/api/model/metrics'),
};
