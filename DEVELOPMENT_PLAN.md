# SubroRecover AI — Development Plan & Execution Checklist

## 1. Project Master Roadmap & Phase Checklist

| Phase | Description | Key Deliverables | Status |
|:---:|:---|:---|:---:|
| **Phase 1** | Requirements & System Architecture | `REQUIREMENTS.md`, `ARCHITECTURE.md`, `DEVELOPMENT_PLAN.md`, Mermaid diagrams | **Completed** |
| **Phase 2** | Workspace & Technology Stack Setup | Directory structure, verified package dependencies, environment templates | **Completed** |
| **Phase 3** | Synthetic Data & Data Engineering Pipeline | Synthetic CSV generators, `ingestion.py`, `cleaning.py`, `transformation.py`, `validation.py`, `database_loader.py`, `monitoring.py`, `pipeline.py` | **In Progress** |
| **Phase 4** | Relational Database Architecture | `database/schema.sql`, `database/connection.py` (PostgreSQL + SQLite dual resilience), 10 relational tables | Pending |
| **Phase 5** | Machine Learning Model | `ml/train.py`, `ml/evaluate.py`, `ml/predict.py`, Random Forest priority classifier, metrics, feature importances | Pending |
| **Phase 6** | RAG Document Intelligence | `rag/document_loader.py`, `rag/chunking.py`, `rag/embeddings.py`, `rag/retriever.py`, ChromaDB integration | Pending |
| **Phase 7** | Multi-Agent AI System | 6 specialized agents: `claim_agent.py`, `evidence_agent.py`, `liability_agent.py`, `recovery_agent.py`, `prioritization_agent.py`, `report_agent.py` | Pending |
| **Phase 8** | LangGraph Orchestration Workflow | `agents/workflow.py`, state definition, sequential and conditional routing, human review checkpoint | Pending |
| **Phase 9** | FastAPI Backend Service | `backend/main.py`, REST endpoints (`/claims`, `/documents`, `/investigate`, `/assessment`, `/reports`, `/analytics`, `/pipeline`, `/model`), Pydantic schemas | Pending |
| **Phase 10** | Enterprise Streamlit Dashboard | `frontend/app.py`, 8 operational pages, Plotly visualizations, enterprise CSS styling | Pending |
| **Phase 11** | ReportLab PDF Report Generation | `reports/report_generator.py`, 14-section formal subrogation investigation report with human review block | Pending |
| **Phase 12** | End-to-End System Integration | Integration of ETL, DB, ML, RAG, Agents, API, Frontend, and PDF generation | Pending |
| **Phase 13** | Testing & Quality Assurance | Automated test suite in `tests/`, end-to-end claim investigation test, regression verification | Pending |
| **Phase 14** | Complete Technical Documentation | Comprehensive docs (`DATA_DICTIONARY.md`, `API_DOCUMENTATION.md`, `AGENT_DOCUMENTATION.md`, `MODEL_DOCUMENTATION.md`, `INSTALLATION_GUIDE.md`, `USER_GUIDE.md`, `LIMITATIONS.md`, `TESTING_REPORT.md`, `README.md`) | Pending |
| **Phase 15** | GitHub Preparation | Clean git repo, license, sanitized files, `.gitignore`, publication instructions | Pending |

---

## 2. Execution Strategy

1. **Autonomous Progression:** Complete each phase sequentially, run targeted tests, verify outputs, fix any discrepancies, and advance immediately without unnecessary prompts.
2. **Deterministic & Resilient Defaults:**
   - Database layer attempts PostgreSQL connection; gracefully falls back to local SQLite database (`subro_recover.db`) if local PostgreSQL authentication is unavailable.
   - AI agent system utilizes Gemini API when `GEMINI_API_KEY` is present in `.env`, and smoothly transitions to deterministic, rule-grounded local analytical simulation when keys are absent, clearly labeling mode in runtime logs.
   - Vector search leverages ChromaDB or dense cosine semantic retrieval.
3. **Enterprise UI Standard:** Streamlit dashboard strictly implements white background, navy `#0F172A` typography, `#2563EB` blue accents, compact KPI cards, and persistent left navigation.

---

## 3. Immediate Next Tasks (Phase 3 & Phase 4)
- Generate rich synthetic datasets in `sample_data/`:
  - `customers.csv` (100+ realistic insured profiles)
  - `policies.csv` (Auto & Commercial P&C policies)
  - `claims.csv` (Auto collision, property damage, rear-end, T-bone, multi-vehicle claims)
  - `accident_reports.csv` (Police incident narratives, citations, adverse driver actions)
  - `involved_parties.csv` (Insured, adverse drivers, adverse insurers)
  - `historical_recoveries.csv` (Past subrogation recovery outcomes for ML training)
  - `evidence_metadata.csv` (Supporting photos, dashcam, police reports)
- Build all 7 modules of `data_engineering/` and verify ETL execution.
- Create `database/schema.sql` and `database/connection.py`.
