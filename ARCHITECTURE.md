# SubroRecover AI — System Architecture Specification

## 1. Executive Summary & Architectural Overview

**SubroRecover AI** is an enterprise-grade, agentic insurance intelligence system engineered to accelerate and automate the subrogation investigation lifecycle for Property & Casualty (P&C) and Commercial Auto insurance carriers.

### The Subrogation Challenge
Subrogation represents the carrier's right to pursue liable third parties for losses paid out to insured policyholders. In practice:
- Billions of dollars in viable recovery are lost annually ("subrogation leakage") due to manual triage bottlenecks.
- Adjusters spend weeks manually reading police accident narratives, repair invoices, and witness accounts.
- Statute of Limitations (SOL) deadlines are tracked inconsistently.
- Estimations of comparative negligence and financial quantum lack objective data grounding.

### The SubroRecover AI Solution
SubroRecover AI is built as a **Decision-Support and Investigation Acceleration Platform**:
- Automated ETL pipeline transforming heterogeneous claim feeds into normalized analytical schemas.
- Dual-database resilience (PostgreSQL production-ready with zero-config SQLite development fallback).
- Supervised Machine Learning model (Random Forest) for predictive case prioritization.
- Contextual Document RAG engine (PyPDF + ChromaDB) for grounded evidentiary fact extraction.
- LangGraph-orchestrated 6-Agent AI system providing explainable, multi-dimensional claim assessments.
- FastAPI REST backend serving claims, assessments, telemetry, and reporting endpoints.
- Streamlit enterprise dashboard delivering an 8-page command center for adjusters and executives.
- ReportLab-powered automated 14-section court-ready Subrogation Investigation PDF generation.

---

## 2. End-to-End System Architecture

```mermaid
flowchart TD
    subgraph INGESTION["1. Data Engineering & Ingestion Layer"]
        RAW_SRC["Raw Sources (CSV, JSON, Claims, Policies, Reports)"]
        INGEST["ingestion.py (File Ingestion)"]
        CLEAN["cleaning.py (Deduplication, Imputation, Normalization)"]
        TRANS["transformation.py (Feature Engineering & Formatting)"]
        VALID["validation.py (Schema & Constraint Verification)"]
        LOADER["database_loader.py (Relational Loading)"]
        MONITOR["monitoring.py (Execution Logs & Data Quality Reports)"]
        
        RAW_SRC --> INGEST --> CLEAN --> TRANS --> VALID --> LOADER
        LOADER --> MONITOR
    end

    subgraph PERSISTENCE["2. Relational & Vector Persistence"]
        LOADER --> DB[("Relational DB (PostgreSQL / SQLite Fallback)")]
        subgraph TABLES["10 Core Tables"]
            T1["customers"]
            T2["insurance_policies"]
            T3["insurance_claims"]
            T4["accident_reports"]
            T5["involved_parties"]
            T6["evidence_documents"]
            T7["recovery_assessments"]
            T8["agent_execution_logs"]
            T9["investigation_reports"]
            T10["human_review_records"]
        end
        DB --- TABLES
        
        DOC_SRC["PDF Documents (Accident Reports, Statements)"] --> RAG_LOAD["rag/document_loader.py & chunking.py"]
        RAG_LOAD --> VEC_DB[("Vector Store (ChromaDB / Embeddings)")]
    end

    subgraph INTELLIGENCE["3. Analytics, ML & Retrieval Subsystems"]
        ML_TRAIN["ml/train.py & evaluate.py (Random Forest Model)"]
        ML_PRED["ml/predict.py (Case Prioritization Engine)"]
        DB --> ML_TRAIN --> ML_PRED
        
        RAG_RET["rag/retriever.py (Contextual Semantic Search)"]
        VEC_DB --> RAG_RET
    end

    subgraph AGENTS_LAYER["4. LangGraph Multi-Agent Orchestration Layer"]
        START_CLAIM["Claim Submitted for AI Investigation"] --> AG1
        
        subgraph AGENTS["Six Specialized AI Agents"]
            AG1["1. Claim Analysis Agent (agents/claim_agent.py)"]
            AG2["2. Evidence Analysis Agent (agents/evidence_agent.py)"]
            AG3["3. Liability Assessment Agent (agents/liability_agent.py)"]
            AG4["4. Recovery Estimation Agent (agents/recovery_agent.py)"]
            AG5["5. Case Prioritization Agent (agents/prioritization_agent.py)"]
            AG6["6. Investigation Report Agent (agents/report_agent.py)"]
        end
        
        AG1 -->|Claim Summary & Missing Fields| AG2
        AG2 -->|Extracted Parties & Evidence Grounding| AG3
        AG3 -->|Liability Splits & Third-Party Fault| AG4
        AG4 -->|Net Recovery Exposure Range| AG5
        AG5 -->|ML Priority & Urgency Score| AG6
        AG6 --> HITL["Human-in-the-Loop Review Gate"]
        
        AG2 <--> RAG_RET
        AG5 <--> ML_PRED
    end

    subgraph BACKEND_LAYER["5. FastAPI REST API Layer"]
        API["FastAPI Backend (backend/main.py)"]
        API --> DB
        API --> AGENTS_LAYER
        API --> RPT_GEN["reports/report_generator.py (ReportLab PDF)"]
    end

    subgraph PRESENTATION["6. Enterprise Presentation Layer"]
        ST_APP["Streamlit Enterprise Dashboard (frontend/app.py)"]
        ST_APP --> API
        ST_APP --> DB
        
        subgraph PAGES["8 Dashboard Modules"]
            P1["1. Executive Overview"]
            P2["2. Claims Management"]
            P3["3. AI Investigation Workspace"]
            P4["4. Recovery Intelligence"]
            P5["5. Document Intelligence"]
            P6["6. Investigation Reports"]
            P7["7. Data Pipeline Monitoring"]
            P8["8. Model Performance"]
        end
        ST_APP --- PAGES
        
        ADJUSTER["Claims Adjuster / Subrogation Specialist"] <--> ST_APP
    end
```

---

## 3. Multi-Agent Orchestration Workflow (LangGraph)

The platform implements six specialized cooperative agents orchestrated via **LangGraph**:

```mermaid
sequenceDiagram
    autonumber
    actor Adjuster as Claims Adjuster (HITL)
    participant Orchestrator as LangGraph Orchestrator (workflow.py)
    participant ClaimAgent as Agent 1: Claim Analysis
    participant EvidenceAgent as Agent 2: Evidence Analysis
    participant LiabilityAgent as Agent 3: Liability Assessment
    participant RecoveryAgent as Agent 4: Recovery Estimation
    participant PriorityAgent as Agent 5: Case Prioritization
    participant ReportAgent as Agent 6: Investigation Report
    participant ReportLab as PDF Engine (report_generator.py)

    Adjuster->>Orchestrator: Trigger Investigation(claim_id)
    Orchestrator->>ClaimAgent: Execute(claim_data)
    ClaimAgent-->>Orchestrator: ClaimSummary, validation_flags, missing_fields
    
    Orchestrator->>EvidenceAgent: Execute(claim_summary, documents, RAG context)
    EvidenceAgent-->>Orchestrator: involved_parties, evidence_citations, facts vs unverified
    
    Orchestrator->>LiabilityAgent: Execute(incident_facts, adverse_driver_actions)
    LiabilityAgent-->>Orchestrator: liability_split, third_party_fault_pct, negligence_reasoning
    
    Orchestrator->>RecoveryAgent: Execute(paid_claim, deductible, fault_pct)
    RecoveryAgent-->>Orchestrator: gross_recoverable, net_recoverable, make_whole_breakdown
    
    Orchestrator->>PriorityAgent: Execute(claim_features, ML Model prediction)
    PriorityAgent-->>Orchestrator: priority_tier (High/Med/Low), confidence, driver_factors
    
    Orchestrator->>ReportAgent: Execute(all_prior_agent_outputs)
    ReportAgent-->>Orchestrator: executive_summary, recommended_actions, investigation_dossier
    
    Orchestrator->>ReportLab: GenerateInvestigationPDF(dossier)
    ReportLab-->>Orchestrator: Generated PDF artifact path
    
    Orchestrator-->>Adjuster: Assessment Complete & Ready for Human Decision
    Adjuster->>Orchestrator: Submit Review Decision (Approved / Flagged / Rejected)
```

---

## 4. Architectural Component Responsibilities

### 4.1 Data Engineering (`data_engineering/`)
- `ingestion.py`: Connectors for CSV, JSON, and raw claim feeds.
- `cleaning.py`: Deduplication, missing value imputation, data type casting, date normalization.
- `transformation.py`: Derived feature creation (recovery percentages, days-to-report, party ratios).
- `validation.py`: Business rule constraint assertions (paid_amount > 0, valid policy dates).
- `database_loader.py`: Batch relational loaders with transaction safety and UPSERT capability.
- `monitoring.py`: ETL job telemetry, processing throughput, error counters, and quality summaries.
- `pipeline.py`: Master ETL orchestrator coordinating extraction, transformation, validation, and loading.

### 4.2 Database Layer (`database/`)
- `schema.sql`: DDL defining all 10 relational tables, indexes, check constraints, and foreign key cascades.
- `connection.py`: Resilient SQLAlchemy engine manager auto-selecting PostgreSQL (when reachable) or local SQLite (`subro_recover.db`).

### 4.3 Machine Learning (`ml/`)
- `train.py`: Trains a Scikit-learn Random Forest classifier on historical claim recovery profiles.
- `evaluate.py`: Generates test set confusion matrix, classification report, ROC-AUC score, and feature importances.
- `predict.py`: Reusable inference pipeline providing priority scores and explainability factors.
- `models/`: Serialized model binaries (`rf_priority_model.joblib`) and metadata.

### 4.4 RAG Document Intelligence (`rag/`)
- `document_loader.py`: PDF document parser extracting text with layout awareness.
- `chunking.py`: Semantic chunker with configurable token overlap to preserve incident context.
- `embeddings.py`: Vector embeddings generator supporting ChromaDB integration.
- `retriever.py`: Context-grounded retriever returning top matching excerpts with source citations.

### 4.5 Agentic AI Layer (`agents/`)
- `claim_agent.py`: Validates coverage, verifies paid claim limits, flags deductible gaps.
- `evidence_agent.py`: Audits police narratives, identifies citations, cross-references statements.
- `liability_agent.py`: Evaluates comparative fault split based on statutory negligence rules.
- `recovery_agent.py`: Computes net recoverable quantum with Make-Whole policyholder protection.
- `prioritization_agent.py`: Applies ML model scores and assigns investigation urgency tiers.
- `report_agent.py`: Compiles unified findings, missing data checklists, and actionable recommendations.
- `workflow.py`: LangGraph state machine coordinating linear and conditional agent workflows.

### 4.6 Backend API (`backend/`)
- `main.py`: FastAPI application entrypoint with CORS, logging middleware, and health endpoints.
- `api/`: REST routing modules for claims, documents, investigation triggers, reports, analytics, and telemetry.
- `schemas/`: Pydantic validation schemas for API inputs and responses.
- `services/`: Business services connecting agents, DB, ML, and PDF generator.

### 4.7 Frontend Dashboard (`frontend/`)
- `app.py`: Streamlit multi-page enterprise dashboard entry point.
- `pages/`: 8 purpose-built adjuster and management modules with Plotly analytics.
- `components/`: Reusable enterprise UI cards, tables, badges, and callouts.
- `assets/`: Custom enterprise CSS styling adhering strictly to corporate design guidelines.

### 4.8 Reporting (`reports/`)
- `report_generator.py`: Generates official, multi-page Subrogation Investigation Reports via ReportLab with corporate branding, tables, metrics, and human sign-off blocks.

---

## 5. Security, Privacy & Design Safeguards

1. **Zero Secret Leakage:** Database credentials and LLM keys are accessed exclusively via `.env`.
2. **Transparent Local Fallbacks:** System operates seamlessly offline without external API dependencies.
3. **Auditability:** Every agent execution, state mutation, and human decision is persisted with timestamps.
4. **Human Governance:** AI outputs are presented strictly as decision-support intelligence.
