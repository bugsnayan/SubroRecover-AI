# SubroRecover AI — Multi-Agent Architecture Documentation

## 1. Overview & Architectural Philosophy

SubroRecover AI replaces manual, fragmented claims reviews with a coordinated **StateGraph** of six specialized, single-responsibility AI agents orchestrated via **LangGraph**.

Each agent operates on a strongly-typed shared state model (`SubroRecoverState`), emitting auditable logs, execution metrics, and provenance citations into the relational database (`agent_execution_logs`).

```
Claim Submission
      ↓
[Agent 1: Claim Analysis Agent]
      ↓ (Claim Summary & Missing Fields)
[Agent 2: Evidence Analysis Agent] <--> [ChromaDB RAG Engine]
      ↓ (Verified Facts, Citations & Parties)
[Agent 3: Liability Assessment Agent] <--> [State Negligence Doctrines]
      ↓ (Comparative Fault Splits)
[Agent 4: Recovery Estimation Agent] <--> [Make-Whole Financial Algorithm]
      ↓ (Gross & Net Quantum Ranges)
[Agent 5: Case Prioritization Agent] <--> [Random Forest ML Inference]
      ↓ (Priority Level & Triage Urgency)
[Agent 6: Investigation Report Agent] --> [Database Persistence & PDF Engine]
      ↓
[Human-in-the-Loop Review Gate]
```

---

## 2. Specialized Agent Profiles

### 2.1 Agent 1: Claim Analysis Agent (`agents/claim_agent.py`)
- **Objective:** Analyzes raw first-party claim records, verifies coverage active dates, validates paid amounts against policy limits, and flags missing documentation fields.
- **Inputs:** `claim_data`, `policy_data`, `customer_data`.
- **Outputs:** `claim_summary`, `claim_validation_status` (`VALID` / `INCOMPLETE`), `missing_claim_fields`.
- **Key Logic:** Ensures carrier paid loss is non-negative, deductible is accounted for, and verifies whether loss magnitude justifies subrogation pursuit ($> $500 threshold).
- **Execution Mode:** Invokes Google Gemini when `GEMINI_API_KEY` is present; smoothly falls back to deterministic rule extraction when unconfigured.

---

### 2.2 Agent 2: Evidence Analysis Agent (`agents/evidence_agent.py`)
- **Objective:** Conducts evidentiary audits across police accident narratives, certified repair invoices, and witness accounts using semantic RAG retrieval.
- **Inputs:** `claim_summary`, `accident_report_data`, `involved_parties`, `evidence_documents`.
- **Outputs:** `verified_facts`, `unverified_facts`, `evidence_citations`, `evidence_sources`, `conflicting_information`.
- **Key Logic:**
  - Performs semantic vector search on ChromaDB for statutory violations (e.g. "Following Too Closely", "Red Light Disregard").
  - Strictly distinguishes verified facts (from official law enforcement records) from self-reported claims.
  - Flags conflicting statements between adverse and insured drivers.

---

### 2.3 Agent 3: Liability Assessment Agent (`agents/liability_agent.py`)
- **Objective:** Evaluates comparative fault splits grounded in statutory negligence doctrines across US jurisdictions.
- **Inputs:** `claim_summary`, `evidence_analysis`, `verified_facts`, `evidence_citations`.
- **Outputs:** `adverse_fault_pct`, `insured_fault_pct`, `negligence_doctrine`, `is_third_party_liable`, `liability_rationale`.
- **Jurisdiction Mapping:**
  - *Modified Comparative (51% Bar)* (TX, FL, IL, OH): Adverse fault must equal or exceed 51% to recoup damages.
  - *Modified Comparative (50% Bar)* (GA): Adverse fault must exceed 50%.
  - *Pure Comparative* (CA, AZ): Recovery proportional to adverse fault regardless of threshold.
- **Ethical Safeguard:** Findings are explicitly framed as decision-support assessments, not binding legal rulings.

---

### 2.4 Agent 4: Recovery Estimation Agent (`agents/recovery_agent.py`)
- **Objective:** Calculates financial recovery exposure, collection feasibility, and strictly honors the **Make-Whole Doctrine** for insured policyholders.
- **Inputs:** `paid_loss_amount`, `deductible_amount`, `adverse_fault_pct`, `is_third_party_liable`.
- **Outputs:** `gross_recovery_estimate`, `net_carrier_recovery`, `insured_deductible_recovery`, `estimated_collection_cost`, `quantum_rationale`.
- **Financial Algorithm:**
  $$\text{Gross Potential} = (\text{Paid Loss} + \text{Deductible}) \times \text{Adverse Fault} \%$$
  $$\text{Deductible Refund (Make-Whole)} = \text{Deductible} \times \text{Adverse Fault} \%$$
  $$\text{Collection Overhead} = (\text{Paid Loss} \times \text{Adverse Fault} \%) \times 0.05 \quad (\text{for losses } > \$2,000)$$
  $$\text{Net Carrier Recovery} = (\text{Paid Loss} \times \text{Adverse Fault} \%) - \text{Collection Overhead}$$

---

### 2.5 Agent 5: Case Prioritization Agent (`agents/prioritization_agent.py`)
- **Objective:** Integrates the trained Scikit-learn Random Forest model to predict recovery urgency and triage priority tier.
- **Inputs:** Claim features (paid loss, claimed loss, adverse fault %, citations, police report flag, days to report).
- **Outputs:** `priority_level` (`High`, `Medium`, `Low`), `priority_score` (confidence 0-1), `contributing_factors`, `recommended_sla_days`.
- **Operational SLA Mapping:**
  - `High Priority`: 5-day expedited subrogation demand package.
  - `Medium Priority`: 14-day standard investigation and witness statement acquisition.
  - `Low Priority`: 30-day review or administrative closure without pursuit.

---

### 2.6 Agent 6: Investigation Report Agent (`agents/report_agent.py`)
- **Objective:** Consolidates all agent outputs into a unified, court-ready 14-section investigation dossier.
- **Inputs:** Complete accumulated `SubroRecoverState`.
- **Outputs:** `executive_summary`, `recommended_actions`, `missing_documentation_checklist`, `report_id`, relational database persistence in `recovery_assessments` and `investigation_reports`.
- **Integration:** Directly prepares payload for ReportLab PDF compilation.

---

## 3. LangGraph Orchestration & Human-in-the-Loop Governance

- **State Graph Implementation:** Configured using `langgraph.graph.StateGraph` in `agents/workflow.py`.
- **Execution Tracing:** Every agent transition measures runtime duration in milliseconds and logs input/output payloads to `agent_execution_logs`.
- **Human Governance Gate:** The workflow pauses at completion, requiring an authorized claims adjuster to inspect the dossier, adjust liability splits if desired, and provide an explicit decision (`Approved`, `Modified`, `Rejected`) before issuing demand letters.
