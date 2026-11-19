# SubroRecover AI — User & Adjuster Operations Guide

## 1. Introduction

Welcome to **SubroRecover AI**, the enterprise intelligence platform for insurance claims subrogation and recovery. This guide walks claims adjusters, subrogation specialists, and operational leaders through the platform's core workflows.

---

## 2. Navigating the Enterprise Command Center

The application features a persistent left navigation sidebar with eight specialized modules:

1. **Executive Overview:** Real-time visibility into portfolio loss exposures, projected recovery yields, triage priority distributions, and recent investigation activity.
2. **Claims Management:** Searchable claims registry. Filter claims by status, incident type, or keyword; inspect policyholder coverage limits and deductible balances; upload new PDF crash reports.
3. **AI Investigation Workspace:** The operational cockpit where adjusters trigger the 6-agent reasoning pipeline, inspect step-by-step progress, review evidence facts vs. citations, evaluate Make-Whole financial breakdowns, and record authorized governance decisions.
4. **Recovery Intelligence:** Interactive financial analytics breaking down adverse comparative fault allocations, estimated recovery yields, and ML priority scoring.
5. **Document Intelligence:** Natural language semantic search across all indexed claim documents using ChromaDB vector retrieval. Review verified officer citations and unverified statements with provenance citations.
6. **Investigation Reports:** Library of generated formal investigation reports with one-click ReportLab PDF export.
7. **Data Pipeline Monitoring:** Operational telemetry for the ETL pipeline tracking record processing counts, deduplication, runtime latency, and data quality audits.
8. **Model Performance:** Machine learning explainability center displaying Random Forest accuracy, confusion matrix, ROC-AUC curve, and feature importance rankings.

---

## 3. Step-by-Step Subrogation Investigation Workflow

```
1. Select Claim File in Claims Management or Investigation Workspace
                           ↓
2. Trigger "Run LangGraph Multi-Agent Investigation"
                           ↓
3. Review Agent Findings:
   - Agent 1: Coverage Limits & Paid Outlays
   - Agent 2: Police Narrative & Citations (RAG)
   - Agent 3: Statutory Comparative Fault Split
   - Agent 4: Net Carrier Recovery & Insured Deductible Make-Whole
   - Agent 5: ML Urgency Tier (High / Medium / Low)
   - Agent 6: Recommended Actions & Missing Docs Checklist
                           ↓
4. Human-in-the-Loop Governance Decision:
   - Select: Approved / Modified / Rejected / Escalate
   - Enter Adjuster Justification Notes & Authorized Signature
                           ↓
5. Download Branded 14-Section PDF Subrogation Demand Package
```

---

## 4. Understanding Make-Whole Financial Quantum Calculations

Under standard insurance law (the **Make-Whole Doctrine**), an insured policyholder must be reimbursed for their out-of-pocket deductible before the carrier retains subrogation proceeds.

SubroRecover AI models this automatically:
- **Total Exposure:** $\text{Paid Loss} + \text{Deductible}$
- **Gross Recovery:** $\text{Total Exposure} \times \text{Adverse Fault} \%$
- **Insured Make-Whole Refund:** $\text{Deductible} \times \text{Adverse Fault} \%$
- **Estimated Collection Overhead:** $5\%$ of carrier gross (reserves for arbitration/processing)
- **Net Carrier Recovery:** $(\text{Paid Loss} \times \text{Adverse Fault} \%) - \text{Collection Overhead}$

---

## 5. Decision Governance & Ethical Boundaries

> [!IMPORTANT]
> **SubroRecover AI is a Decision-Support System.**
> 
> - It does **not** establish binding legal fault.
> - It does **not** guarantee financial recovery from adverse carriers.
> - All demand letters and subrogation closures must be reviewed and authorized by an approved claims professional.
