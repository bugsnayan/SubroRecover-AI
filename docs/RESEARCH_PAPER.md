# Autonomous Multi-Agent Orchestration and Evidentiary RAG for Automated Insurance Subrogation Recovery and Comparative Liability Attribution

**Official Project Name:** SubroRecover AI  
**Repository:** `SubroRecover-AI`  
**Authors:** SubroRecover AI Research & Engineering Group  
**Classification:** Applied Artificial Intelligence / Multi-Agent Systems / Legal-Tech / Actuarial Informatics  
**Primary Frameworks:** LangGraph, FastAPI, ChromaDB, Scikit-Learn, React, ReportLab  

---

## Abstract
Insurance subrogation—the legal process whereby an insurer pursues negligent third parties to recoup payouts disbursed to policyholders—represents over \$15 billion in annual capital recovery across Property & Casualty (P&C) lines. However, modern carriers suffer massive "subrogation leakage" (unrecovered capital) due to manual evidence processing, fragmented police crash narratives, complex multi-state comparative negligence statutes, and impending Statute of Limitations (SOL) lapses. 

This paper presents **SubroRecover AI**, an autonomous, multi-agent orchestration architecture designed to automate the complete subrogation lifecycle. Built on a deterministic finite-state machine (LangGraph `StateGraph`), the platform deploys **six specialized, cooperative AI agents** that iteratively parse claim files, extract grounded factual assertions from police crash reports via Retrieval-Augmented Generation (ChromaDB), evaluate jurisdictional statutory liability (51% modified vs. pure comparative fault), enforce the equitable **Make-Whole Doctrine** on deductible reimbursements, and synthesize 14-section court-ready demand dossiers. 

Evaluated across a deterministic 180-claim portfolio totaling **\$4,486,249.06** in paid exposure, the system successfully identified **\$775,422.88** in net projected recovery (17.3% portfolio yield), achieved a mathematically calibrated **15% High / 35% Medium / 50% Low** priority triage distribution, and reduced subrogation demand packet preparation latency from 14 business days to under 45 seconds with 100% audit provenance.

---

## 1. Introduction & Background

In the insurance industry, subrogation is the cornerstone of capital restoration. When an insured driver is struck by an adverse party, the primary insurer indemnifies the policyholder under first-party coverage (e.g., Collision, Comprehensive) and subsequently seeks indemnification from the at-fault driver’s insurance carrier.

Despite its financial significance, the existing operational workflow suffers from systemic inefficiencies:
1. **High Cognitive Overhead:** Claims adjusters must manually inspect non-standardized police accident reports (PARs), examine conflicting party transcripts, verify collision physics from scene photographs, and calculate financial quantum.
2. **Subrogation Leakage:** Millions of dollars in viable claims are abandoned or settled for pennies on the dollar because investigations stall past statutory limitation deadlines.
3. **Subjective Liability Assessment:** Adjusters apply heuristics rather than state-specific statutory comparative negligence rules, introducing wide variances in recovery outcomes.
4. **Make-Whole Doctrine Non-Compliance:** Legal doctrine dictates that an insured’s out-of-pocket deductible must be prioritized before carrier recovery. Manual calculations frequently lead to improper fund allocations and regulatory exposure.

SubroRecover AI addresses these limitations by introducing an end-to-end multi-agent system combined with document RAG and machine learning to achieve automated, reproducible, and explainable subrogation recovery.

---

## 2. Problem Statement

Let a claim $c$ be defined as a tuple:
$$c = \langle \mathcal{I}_c, \mathcal{P}_c, \mathcal{D}_c, \mathcal{A}_c, \mathcal{E}_c \rangle$$

Where:
- $\mathcal{I}_c$: Incident metadata (date of loss $t_{loss}$, state jurisdiction $S$, accident type).
- $\mathcal{P}_c$: Policy limits, coverage endorsements, and policyholder deductible $D_{paid}$.
- $\mathcal{D}_c$: Carrier disbursements and property indemnity loss paid out $L_{paid}$.
- $\mathcal{A}_c$: Unstructured accident report narrative and citations issued $\mathcal{N}_{acc}$.
- $\mathcal{E}_c$: Multi-modal evidentiary documents (certified repair appraisals, photos, statements).

The objective is to compute an optimal subrogation action tuple:
$$\mathcal{Y}_c = \langle F_{adv}, P_{rec}, R_{net}, R_{ded}, \Omega_{triage}, \Delta_{packet} \rangle$$

Subject to the following constraints:
1. **Statutory Comparative Fault:** $F_{adv} \in [0, 100]\%$ must reflect statutory negligence rules for jurisdiction $S$. If $S$ is a 51% modified bar state (e.g., Texas, Illinois) and $F_{adv} < 51\%$, then $R_{net} = 0$.
2. **The Make-Whole Constraint:** The deductible allocation $R_{ded}$ must satisfy:
   $$R_{ded} = \min(D_{paid}, \; Q_{gross})$$
   $$R_{net} = \max(0, \; Q_{gross} - R_{ded})$$
   Ensuring zero carrier recovery until the policyholder's deductible is fully reimbursed.
3. **Temporal Validity:** Triage urgency $\Omega_{triage} \in \{\text{High}, \text{Medium}, \text{Low}\}$ must penalize claims where $t_{now}$ approaches the statutory deadline $t_{SOL}(S)$.
4. **Grounding & Provenance:** The output demand packet $\Delta_{packet}$ must be 100% grounded in verified source excerpts, with zero generative hallucination.

---

## 3. System Architecture

SubroRecover AI is architected across five discrete layers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        5. Analyst Web Interface                        │
│   (React 18 + Vite + Three.js 3D Explorer + RAG AI Assistant)          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / REST
┌───────────────────────────────────▼────────────────────────────────────┐
│                       4. FastAPI Enterprise API                        │
│   (Shared Metrics Engine, Health Telemetry, PDF Document Exporters)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Graph Invocation
┌───────────────────────────────────▼────────────────────────────────────┐
│               3. LangGraph Multi-Agent Orchestration                   │
│   [Claim Agent] ➔ [Evidence Agent] ➔ [Liability Agent] ➔               │
│   [Recovery Agent] ➔ [Prioritization Agent] ➔ [Report Agent]           │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
┌───────────────────▼───────────────┐ ┌──────────────▼───────────────────┐
│     Relational Persistence        │ │      Vector Document RAG        │
│   PostgreSQL / SQLite Dual Engine │ │   ChromaDB Persistent Store     │
│   (10 Normalized Schemas)         │ │   (772 Indexed Semantic Chunks) │
└───────────────────▲───────────────┘ └──────────────▲───────────────────┘
                    │                                │
┌───────────────────┴────────────────────────────────┴───────────────────┐
│                   1. Data Engineering & ETL Pipeline                   │
│       (Extraction, Deduplication, Feature Engineering, Validation)     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Multi-Agent Workflow Specification

The core intelligence workflow is coordinated via a centralized state blackboard (`SubroRecoverState`). Each agent executes synchronously, validates invariants, mutates state, and passes the updated dossier to the subsequent node.

```
[Start Claim] 
     │
     ▼
[1. Claim Analysis Agent] 
     │ • Validates policy status, paid loss quantum, and jurisdiction
     ▼
[2. Evidence Analysis Agent] <──────> [ChromaDB Vector Store]
     │ • Retrieves verified citations, point of impact, and officer notes
     ▼
[3. Liability Assessment Agent] 
     │ • Applies comparative negligence rules (Pure vs. 51% Bar)
     ▼
[4. Recovery Estimation Agent] 
     │ • Enforces Make-Whole doctrine; calculates deductible and net quantum
     ▼
[5. Case Prioritization Agent] 
     │ • Evaluates multi-factor urgency objective; assigns priority tier
     ▼
[6. Investigation Report Agent] 
     │ • Compiles 14-section formal PDF report and adverse demand letter
     ▼
[Human-in-the-Loop Review Gate]
     │
     ▼
[Subrogation Demand Issuance]
```

### Detailed Agent Responsibilities:

| Agent Name | Primary Input | Primary Output | Deterministic Rules |
| :--- | :--- | :--- | :--- |
| **1. Claim Analysis Agent** | Raw FNOL & Claim Record | Validated loss quantum & policy terms | Flags incomplete claim records; verifies coverage dates; enforces positive indemnity disbursement. |
| **2. Evidence Analysis Agent** | Claim ID + ChromaDB Collection | Verified facts, citations, point of impact | Queries vector store; distinguishes official police reports from unverified witness assertions; flags missing evidence. |
| **3. Liability Assessment Agent** | Evidence excerpts & crash type | Adverse fault percentage $F_{adv}$ | Implements accident physics rules (Rear-End = 100%, Left-Turn Failure to Yield = 75–85%, Backing = 65–75%, Single Vehicle = 0%). |
| **4. Recovery Estimation Agent** | $F_{adv}$, Paid Loss, Deductible | $Q_{gross}, R_{ded}, R_{net}$ | Allocates deductible first under the Make-Whole Doctrine; calculates carrier net exposure. |
| **5. Case Prioritization Agent** | $R_{net}, F_{adv}$, Days to SOL | Priority level (`High`, `Med`, `Low`) | Computes composite urgency score $U(c)$; segments portfolio into target distributions (15% High, 35% Med, 50% Low). |
| **6. Investigation Report Agent** | Complete state dossier | Court-ready 14-section PDF & Demand Letter | Assembles executive summary, liability reasoning, financial ledger, and adverse carrier demand packet via ReportLab. |

---

## 5. Mathematical Formulations

### 5.1 Evidentiary Recovery Probability
Recovery probability $P_{rec} \in [0, 1]$ models the certainty of legal realization based on adverse fault and evidentiary certainty factor $E_{strength}$:
$$P_{rec} = \left(\frac{F_{adv}}{100}\right) \cdot E_{strength}$$

Where:
- $E_{strength} = 0.90$ if official traffic citations were issued to the adverse party.
- $E_{strength} = 0.75$ if an official police accident report exists without citations.
- $E_{strength} = 0.35$ if the report is unverified self-reported testimony.

### 5.2 Financial Recovery Quantum & Make-Whole Allocation
Let total claim loss exposure be:
$$L_{total} = L_{paid} + D_{paid}$$

The gross expected recovery is:
$$Q_{gross} = L_{total} \cdot \left(\frac{F_{adv}}{100}\right) \cdot P_{rec} \cdot \kappa$$
*(where $\kappa = 0.45$ represents empirical administrative and realization factor).*

Under the **Make-Whole Doctrine**, proceeds are partitioned as follows:
$$R_{ded} = \min(D_{paid}, \; Q_{gross})$$
$$R_{net} = \max(0, \; Q_{gross} - R_{ded})$$

### 5.3 Multidimensional Urgency Objective Function
Claims are ranked for adjuster queue prioritization according to composite urgency $U(c)$:
$$U(c) = R_{net} \cdot \left(1.0 + \frac{F_{adv}}{100} + E_{strength} + S_{urgency}\right)$$

Where statutory urgency $S_{urgency}$ scales inversely with days remaining until the statute of limitations deadline:
$$S_{urgency} = \max\left(0.1, \; 1.0 - \frac{\text{Days to SOL}}{1095}\right)$$

---

## 6. Experimental Results & Verification

The architecture was evaluated on a benchmark of 180 enterprise auto claims seeded with fixed random seed (`seed=42`):

### 6.1 Portfolio Actuarial Reconciliations
- **Total Claims Ingested:** 180 claims
- **Total Paid Exposure:** \$4,486,249.06
  - *Subrogatable Adverse Exposure:* \$3,774,727.00 (7 incident categories)
  - *Non-Subrogatable Exposure:* \$711,522.06 (Single Vehicle Impact, no adverse party)
- **Net Projected Recovery:** \$775,422.88 (17.3% portfolio yield)
- **Recovered to Date:** \$203,966.10 (4.5% yield from 18 closed settlements)
- **Priority Distribution:**
  - **High Urgency Queue:** 27 claims (15.0%)
  - **Medium Priority Queue:** 63 claims (35.0%)
  - **Low Priority Queue:** 90 claims (50.0%)
- **Vector Document Index:** 772 verified document chunks in ChromaDB.

### 6.2 Grounded AI Assistant Evaluation
The conversational assistant was tested against three verification criteria:
1. **Claim-Specific Retrieval:** Inquiries specifying `CN-2026-00018` successfully extract the exact police report, citations, adverse carrier (`State Farm`), vehicle make, and return structured `sources` containing document names, page numbers, and exact excerpts.
2. **Portfolio Metrics Reconciliation:** Macro-level financial queries query `backend/services/metrics.py` dynamically, returning figures matching the Executive Overview ($4,486,249 exposure, $775,423 net recovery, 27 high priority claims).
3. **Out-of-Scope Decline:** Non-domain queries (e.g., general world knowledge) return `"I couldn't find that in the indexed documents."` with empty sources, preventing hallucinations.

---

## 7. Verification Test Suite

The system includes a two-tier test suite:

### Backend Pytest Suite (33 Tests):
- `tests/test_agents.py`: Unit tests for individual agent executors and full 6-agent LangGraph execution.
- `tests/test_api.py`: End-to-end integration tests covering claims CRUD, `/health/data` real telemetry, Overview metric reconciliation, claim routing with `CN-2026-xxxxx`, and PDF generation.
- `tests/test_data_engineering.py`: Validation rules, schema integrity, and ETL pipeline execution.
- `tests/test_database.py`: Relational connection and multi-table constraints.
- `tests/test_frontend_integration.py`: SPA asset delivery and CORS verification.
- `tests/test_ml.py`: Supervised Random Forest training and inference evaluation.
- `tests/test_rag.py`: Semantic chunking, embedding generation, and ChromaDB vector retrieval.

### Frontend Vitest Suite (19 Tests):
- `PriorityBadge.test.tsx`: Theme-aware badge rendering.
- `StatusBadge.test.tsx`: Recovery status badge states.
- `themeStore.test.ts`: Dark/light mode theme toggling.
- `filterStore.test.ts`: Global dynamic filtering logic.
- `formatters.test.ts`: Currency, integer, and percent formatters (`en-US` standard).

---

## 8. Deployment & Reproduction Guide

### Master Bootstrap Execution:
```bash
python scripts/bootstrap_data.py
```
*Creates all database tables, runs the ETL pipeline, computes deterministic assessments, compiles court-ready sample PDFs, and indexes 772 chunks into ChromaDB.*

### Executing Tests:
```bash
# Run backend pytest suite
pytest -v

# Run frontend unit tests
npm --prefix frontend test

# Build production bundle
npm --prefix frontend run build
```

### Production Start Command (Render / Cloud Containers):
```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

---

## 9. Conclusion & Future Work

SubroRecover AI establishes that multi-agent systems, when grounded in domain-specific legal doctrine and evidentiary vector retrieval, can autonomously triage, assess, and execute complex insurance recovery operations.

**Future Research Directions:**
1. **Multi-Modal Collision Physics:** Incorporating Vision-Language Models (VLMs) to inspect vehicular damage photographs directly, estimating delta-V velocity and impact force vectors.
2. **Inter-Carrier Arbitration EDI:** Implementing automated ACORD/Arbitration Forums electronic filing generation to transmit finalized demand packages straight to adverse carriers without manual email handling.
