# SubroRecover AI — System Requirements Specification (SRS)

## 1. Document Control & Overview

| Attribute | Specification |
|---|---|
| **Project Title** | SubroRecover AI: AI-Powered Multi-Agent Insurance Subrogation & Recovery Intelligence Platform |
| **Document Version** | 1.0.0 (Release Candidate) |
| **Target Organization** | Value Momentum, Hyderabad (Technical Evaluation) |
| **System Classification** | Enterprise Decision-Support System (HITL: Human-in-the-Loop) |
| **Core Architecture** | Multi-Agent AI (LangGraph) + Machine Learning (Scikit-learn) + RAG (ChromaDB) + FastAPI + Streamlit |

---

## 2. Business Problem & Mission

### 2.1 The Subrogation Challenge
Subrogation is the legal right of an insurance carrier to pursue a negligent third party (or adverse insurer) to recover claim expenses paid to an insured policyholder. In Property & Casualty (P&C) and Commercial Auto insurance:
1. **Subrogation Leakage:** An estimated $15 Billion in legitimate subrogation recovery is lost annually due to missed indicators, manual triaging bottlenecks, and delayed document investigation.
2. **Investigation Latency:** Manual review of police accident narratives, repair estimates, and insured/claimant statements typically takes 14 to 28 days per file.
3. **Statute of Limitations (SOL) Risks:** Claims risk forfeiture when statutory filing deadlines (varying by jurisdiction from 1 to 6 years) are tracked in disparate spreadsheets.
4. **Subjective Liability Assessment:** Without objective statutory fault allocation and comparative negligence scoring, claims adjusters often settle for sub-optimal recovery splits.

### 2.2 System Objective
SubroRecover AI provides insurance claims professionals with an automated, auditable, evidence-grounded decision support platform that:
- Ingests structured claims, policies, parties, and unstructured accident reports.
- Extracts key incident factors, driver actions, citations, and damages.
- Flags third-party liability indicators with statutory negligence grounding.
- Estimates net recovery quantum respecting insured deductibles and Make-Whole principles.
- Ranks investigation priority using a trained Machine Learning model.
- Synthesizes findings across 6 specialized AI agents into a court-ready ReportLab investigation PDF.
- Maintains strict human oversight before any external demand is issued.

---

## 3. Critical Business Rules & Governance

> [!IMPORTANT]
> **Decision-Support Constraint:** SubroRecover AI is strictly a decision-support and intelligence acceleration system. It must **NOT**:
> 1. Independently establish binding legal liability.
> 2. Guarantee financial recovery amounts.
> 3. Automatically deny, accept, or close claims without human adjuster approval.
> 4. Fabricate citations, accident facts, or financial numbers.

### Key Business Rules:
- **BR-001 (Human Approval Gate):** All agent recommendations, priority scores, and demand estimates must undergo explicit Human Review before finalizing report generation or dispatch.
- **BR-002 (Fact Grounding):** The system must clearly separate verified facts (sourced directly from police reports or official claims documents) from inferred findings and AI recommendations.
- **BR-003 (Make-Whole Principle):** Deductibles paid by the insured must be accounted for in recovery allocation prior to net carrier reimbursement calculation.
- **BR-004 (Dual Database Resilience):** Production deployments run on PostgreSQL; local development and evaluation support zero-configuration SQLite fallback without feature loss.
- **BR-005 (Graceful LLM Degradation):** When Gemini API keys are unavailable, the agent system must operate in a transparent, deterministic local evaluation mode, explicitly noting mock execution without pretense.

---

## 4. Functional Requirements

### 4.1 Data Engineering & ETL (Module: `data_engineering`)
- **FR-ETL-01 (Multi-Source Ingestion):** Ingest structured datasets covering Customers, Policies, Claims, Involved Parties, Accident Reports, and Historical Recoveries in CSV and JSON formats.
- **FR-ETL-02 (Data Cleaning & Normalization):**
  - Impute or handle missing values in numeric and categorical fields.
  - Eliminate duplicate records based on natural composite keys.
  - Standardize date formats to ISO-8601 (`YYYY-MM-DD`).
  - Validate insurance amounts (paid claim >= 0, deductible >= 0).
- **FR-ETL-03 (Feature Engineering):** Compute derived metrics: `recovery_rate`, `days_to_report`, `party_count`, `has_police_report`, `fault_indicator_score`.
- **FR-ETL-04 (Database Loading & Tracking):** Maintain separate raw ingestion and cleaned/processed schemas. Log execution metrics (records processed, errors, run duration).

### 4.2 Database & Storage (Module: `database`)
- **FR-DB-01 (Relational Tables):** Implement 10 primary relational tables:
  1. `customers`
  2. `insurance_policies`
  3. `insurance_claims`
  4. `accident_reports`
  5. `involved_parties`
  6. `evidence_documents`
  7. `recovery_assessments`
  8. `agent_execution_logs`
  9. `investigation_reports`
  10. `human_review_records`
- **FR-DB-02 (Integrity):** Enforce primary keys, foreign keys, timestamps (`created_at`, `updated_at`), check constraints, and performance indexes on `claim_id` and `customer_id`.
- **FR-DB-03 (Engine Support):** Native support for PostgreSQL with automatic fallback to local SQLite (`subro_recover.db`).

### 4.3 Machine Learning (Module: `ml`)
- **FR-ML-01 (Prioritization Classifier):** Random Forest classifier trained to predict investigation priority (`High`, `Medium`, `Low`) based on claim amount, incident type, number of adverse parties, evidence completeness, police citations, and historical recovery yield.
- **FR-ML-02 (Evaluation & Metrics):** Output test set metrics: Confusion Matrix, Accuracy, Precision, Recall, F1-Score, and ROC-AUC.
- **FR-ML-03 (Explainability):** Extract and expose feature importances to show adjusters which variables drove the priority determination.
- **FR-ML-04 (Model Serialization):** Persist trained model artifacts (`model.joblib`, `scaler.joblib`, `metadata.json`) for backend and dashboard inference.

### 4.4 RAG Document Intelligence (Module: `rag`)
- **FR-RAG-01 (PDF Ingestion & Text Extraction):** Load accident reports, witness statements, and policy forms via `pypdf`.
- **FR-RAG-02 (Chunking & Embedding):** Recursive character chunking (500 tokens with 50 token overlap); embedding generation using ChromaDB / dense similarity.
- **FR-RAG-03 (Contextual Semantic Retrieval):** Retrieve top-k relevant excerpts for liability questions (e.g., "citations issued", "point of impact", "weather conditions").
- **FR-RAG-04 (Attribution & Citation):** Every retrieved claim finding must cite the source document name, chunk ID, and confidence score.

### 4.5 Multi-Agent System (Module: `agents`)
- **FR-AG-01 (Agent 1: Claim Analysis):** Validates policy coverage status, deductibles, paid claim totals, and flags data anomalies.
- **FR-AG-02 (Agent 2: Evidence Analysis):** Analyzes accident reports and witness statements; extracts involved vehicles, drivers, and citations.
- **FR-AG-03 (Agent 3: Liability Assessment):** Computes estimated third-party liability split based on comparative negligence rules without legal finality.
- **FR-AG-04 (Agent 4: Recovery Estimation):** Calculates net recoverable potential: $\text{Recovery} = (\text{Paid Loss} + \text{Deductible}) \times \text{Adverse Fault} \% - \text{Estimated Collection Cost}$.
- **FR-AG-05 (Agent 5: Case Prioritization):** Integrates the trained ML model with heuristic rules to generate investigation priority and triage urgency.
- **FR-AG-06 (Agent 6: Investigation Report):** Aggregates insights from all prior agents into a unified, coherent structured summary with action items.

### 4.6 LangGraph Orchestration (Module: `agents/workflow.py`)
- **FR-LG-01 (State Machine):** Deterministic state graph passing a strongly-typed `SubroState` dictionary/Pydantic model across nodes.
- **FR-LG-02 (Execution Tracing):** Each agent execution emits runtime logs, status flags, and timestamps stored in `agent_execution_logs`.
- **FR-LG-03 (Human Review Checkpoint):** Graph flow pauses or terminates at human review readiness.

### 4.7 FastAPI REST Backend (Module: `backend`)
- **FR-API-01 (REST Endpoints):**
  - `POST /claims`: Submit a new claim.
  - `GET /claims`: List claims with pagination and status filters.
  - `GET /claims/{claim_id}`: Retrieve detailed claim dossier.
  - `POST /claims/{claim_id}/documents`: Upload supporting PDF documents.
  - `POST /claims/{claim_id}/investigate`: Trigger the 6-agent LangGraph workflow.
  - `GET /claims/{claim_id}/assessment`: Fetch the multi-agent assessment outputs.
  - `GET /reports/{report_id}`: Fetch report metadata and PDF download link.
  - `GET /analytics/overview`: High-level portfolio recovery KPIs.
  - `GET /pipeline/status`: Ingestion and ETL health metrics.
  - `GET /model/metrics`: Machine learning model performance benchmarks.

### 4.8 Streamlit Enterprise Dashboard (Module: `frontend`)
- **FR-UI-01 (Design Standard):** Enterprise B2B theme: clean white background, `#0F172A` deep navy typography, `#2563EB` restrained blue accents, compact KPI cards, responsive layout.
- **FR-UI-02 (8 Operational Pages):**
  1. *Executive Overview*: Portfolio metrics, recovery funnel, priority distribution.
  2. *Claims Management*: Interactive claim registry with search, filter, and document upload.
  3. *AI Investigation Workspace*: Real-time agent execution pipeline, interactive outputs, human approval.
  4. *Recovery Intelligence*: Financial exposures, comparative fault splits, ML priority scoring.
  5. *Document Intelligence*: PDF upload, text viewer, RAG semantic search across incident files.
  6. *Investigation Reports*: Generated reports table, status tracking, and PDF download buttons.
  7. *Data Pipeline Monitoring*: ETL run history, validation counts, error logs.
  8. *Model Performance*: ROC-AUC, confusion matrix, precision/recall, feature importance charts.

### 4.9 PDF Investigation Reporting (Module: `reports`)
- **FR-PDF-01 (ReportLab Synthesis):** Generate an official, branded multi-page Subrogation Investigation Report containing:
  1. Report ID & Generation Timestamp
  2. Claim & Policy Dossier
  3. Incident Circumstances Summary
  4. Involved Parties & Insurance Information
  5. Evidentiary Audit & RAG Citations
  6. Comparative Liability Analysis
  7. Net Recovery Quantum Breakdown
  8. Machine Learning Priority Score
  9. Missing Documents & RFI Checklist
  10. Individual Agent Findings Summary
  11. Recommended Next Actions
  12. Human Reviewer Decision Sign-off
  13. Legal Compliance Disclaimer

---

## 5. Non-Functional Requirements

| Metric | Target Requirement |
|---|---|
| **Response Latency** | REST endpoints response time < 250ms (non-agent); Agent workflow execution < 8s. |
| **Data Integrity** | Foreign key referential integrity enforced on all relational transactions. |
| **Security & Privacy** | Zero credential logging; API keys isolated in `.env`; local test mock fallback. |
| **Code Quality & Tests** | Automated test suite (`pytest`) covering ETL, DB, ML, RAG, Agents, and API with >= 80% coverage on core business logic. |
| **Portability** | Operates on Windows, Linux, and macOS in standard Python 3.11+ virtual environments. |
