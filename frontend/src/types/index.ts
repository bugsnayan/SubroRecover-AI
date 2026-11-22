export interface Claim {
  claim_id: string;
  policy_id: string;
  customer_id: string;
  claim_number: string;
  incident_date: string;
  reported_date: string;
  claim_type: string;
  incident_location: string;
  incident_state: string;
  claimed_amount: number;
  paid_amount: number;
  deductible_paid: number;
  claim_status: string;
  subrogation_status: string;
  description: string;
  priority_level?: 'High' | 'Medium' | 'Low';
  recovery_probability?: number;
  net_recovery_estimate?: number;
  adverse_fault_pct?: number;
  statute_of_limitations_date?: string;
}

export interface InvolvedParty {
  party_id: string;
  claim_id: string;
  party_type: string;
  party_name: string;
  phone_number?: string;
  insurance_carrier?: string;
  policy_number?: string;
  vehicle_make?: string;
  vehicle_model?: string;
  vehicle_year?: number;
  drivers_license_state?: string;
}

export interface EvidenceDocument {
  document_id: string;
  claim_id: string;
  document_type: string;
  file_name: string;
  file_path: string;
  file_size_kb?: number;
  page_count?: number;
  extracted_text?: string;
  extraction_confidence?: number;
  is_verified?: boolean;
  created_at?: string;
}

export interface AccidentReport {
  report_id: string;
  claim_id: string;
  police_report_number?: string;
  police_department?: string;
  officer_badge_number?: string;
  incident_datetime?: string;
  weather_conditions?: string;
  road_conditions?: string;
  citations_issued?: string;
  officer_narrative?: string;
}

export interface RecoveryAssessment {
  assessment_id: string;
  claim_id: string;
  priority_level: 'High' | 'Medium' | 'Low';
  priority_score: number;
  estimated_adverse_fault_pct: number;
  gross_recovery_estimate: number;
  net_recovery_estimate: number;
  insured_deductible_recovery: number;
  recovery_probability: number;
  statute_of_limitations_date?: string;
  liability_rationale?: string;
  quantum_rationale?: string;
  missing_evidence?: string;
  status: string;
  created_at?: string;
}

export interface ClaimDossier {
  claim: Claim;
  policy?: {
    policy_id: string;
    policy_number: string;
    policy_type: string;
    coverage_limit: number;
    deductible_amount: number;
    effective_date: string;
    expiration_date: string;
  };
  customer?: {
    customer_id: string;
    first_name: string;
    last_name: string;
    email: string;
    phone: string;
    address: string;
    city: string;
    state: string;
  };
  accident_report?: AccidentReport;
  parties: InvolvedParty[];
  documents: EvidenceDocument[];
  assessment?: RecoveryAssessment;
  reviews?: any[];
  report?: {
    report_id: string;
    report_number: string;
    report_title: string;
    executive_summary: string;
    full_report_json?: any;
    is_approved: boolean;
  };
}

export interface GraphNode {
  id: string;
  type: 'claim' | 'party' | 'evidence' | 'damage';
  label: string;
  sublabel?: string;
  color: string;
  size: number;
  recovery_probability?: number;
  priority?: string;
  status?: string;
  paid_amount?: number;
  net_recovery?: number;
  role?: string;
  is_adverse?: boolean;
  insurance_carrier?: string;
  citations?: string;
  narrative?: string;
  confidence?: number;
  deductible?: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  weight: number;
  label: string;
  color: string;
}

export interface RecoveryGraphData {
  claim_id: string;
  claim_number: string;
  recovery_probability: number;
  adverse_fault_pct: number;
  projected_net_recovery: number;
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface PortfolioPoint {
  id: string;
  claim_id: string;
  claim_number: string;
  incident_type: string;
  incident_state: string;
  paid_amount: number;
  projected_recovery: number;
  recovery_probability: number;
  days_to_sol: number;
  sol_date?: string;
  priority: 'High' | 'Medium' | 'Low';
  status: string;
  fault_pct: number;
  x: number;
  y: number;
  z: number;
  size: number;
  color: string;
}

export interface PortfolioResponse {
  total_points: number;
  axes: {
    x: { label: string; unit: string };
    y: { label: string; unit: string };
    z: { label: string; unit: string };
  };
  points: PortfolioPoint[];
}

export interface KPICardMetric {
  value: number;
  label: string;
  unit: string;
  delta_pct?: number | null;
  sentiment?: 'good' | 'bad' | 'neutral';
  comparison_period?: string | null;
  calculation: string;
  sparkline?: number[];
}

export interface OverviewKPIs {
  claims_ingested: KPICardMetric;
  total_paid_exposure: KPICardMetric;
  projected_recovery: KPICardMetric;
  recovered_to_date: KPICardMetric;
  projected_recovery_rate: KPICardMetric;
  actual_recovery_rate: KPICardMetric;
  high_urgency_demands: KPICardMetric;
  total_claims?: KPICardMetric;
  projected_net_recovery?: KPICardMetric;
  recovery_rate?: KPICardMetric;
}

export interface OverviewData {
  kpis: OverviewKPIs;
  total_claims_analyzed: number;
  potential_recovery_opportunities: number;
  total_paid_exposure: number;
  projected_net_recovery: number;
  priority_distribution: { High: number; Medium: number; Low: number };
  recovery_status_distribution: Record<string, number>;
  recent_activity: Array<{
    claim_id: string;
    claim_number: string;
    claim_type: string;
    incident_state: string;
    paid_amount: number;
    subrogation_status: string;
    incident_date: string;
    priority_level: string;
    net_recovery_estimate: number;
    recovery_probability: number;
  }>;
}

export interface FunnelStage {
  id: string;
  name: string;
  count: number;
  pct_of_ingested: number;
  pct_drop_previous: number;
  conversion_pct?: number;
  description: string;
}

export interface ExposureByTypeItem {
  incident_type: string;
  claim_count: number;
  paid_exposure: number;
  projected_recovery: number;
  avg_recovery_prob: number;
  recovery_yield: number;
  has_adverse_party?: boolean;
  is_subrogatable?: boolean;
  subrogation_eligibility?: string;
}

export interface RecoveryTrendItem {
  month: string;
  claim_count: number;
  paid_exposure: number;
  projected_recovery: number;
  actual_recovery: number;
}

export interface GeographicItem {
  state: string;
  claim_count: number;
  total_exposure: number;
  projected_recovery: number;
  avg_fault: number;
  recovery_rate: number;
}

export interface NeedsAttentionItem {
  claim_id: string;
  claim_number: string;
  incident_type: string;
  incident_state: string;
  paid_amount: number;
  net_recovery: number;
  recovery_prob: number;
  priority: string;
  days_to_sol: number;
  status: string;
  urgency_reason: string;
}

export interface ChatSource {
  title: string;
  claim_id: string;
  page: number;
  snippet: string;
  relevance_score: number;
  is_verified: boolean;
}

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
  suggested_questions: string[];
  referenced_claims: string[];
}

export interface ReportItem {
  report_id: string;
  claim_id: string;
  claim_number: string;
  report_number: string;
  report_title: string;
  incident_type: string;
  incident_state: string;
  paid_amount: number;
  net_recovery: number;
  priority: string;
  executive_summary: string;
  is_approved: boolean;
  created_at: string;
  download_url: string;
}

export interface ModelMetrics {
  metrics: {
    accuracy: number;
    precision_macro: number;
    recall_macro: number;
    f1_macro: number;
    roc_auc_ovr: number;
    cv_f1_mean: number;
    cv_f1_std: number;
    training_samples: number;
    test_samples: number;
  };
  classification_report: Record<string, any>;
  confusion_matrix: number[][];
  classes: string[];
  feature_importances: Array<{
    feature: string;
    importance: number;
  }>;
}
