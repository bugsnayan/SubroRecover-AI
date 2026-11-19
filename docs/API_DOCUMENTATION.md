# SubroRecover AI — REST API Documentation

The SubroRecover AI backend is implemented in FastAPI, providing performant, asynchronous RESTful endpoints with Pydantic v2 data validation, request timing middleware, CORS, and comprehensive OpenAPI 3.0 documentation.

- **Interactive Swagger Documentation:** `http://127.0.0.1:8000/docs`
- **ReDoc Interface:** `http://127.0.0.1:8000/redoc`

---

## 1. Claims Management Endpoints

### 1.1 `GET /claims`
Retrieve a paginated, filterable list of insurance claims.

**Query Parameters:**
- `limit` (int, default=50): Maximum number of records to return (1-200).
- `offset` (int, default=0): Pagination offset index.
- `status` (string, optional): Filter by operational claim status (`Open`, `In Review`, `Settled`).
- `subro_status` (string, optional): Filter by subrogation state (`Identified`, `Demand Ready`, `In Triage`).
- `search` (string, optional): Substring match across `claim_id`, `claim_number`, or `description`.

**Sample Response (`200 OK`):**
```json
[
  {
    "claim_id": "CLM-0001",
    "policy_id": "POL-0001",
    "customer_id": "CUST-0001",
    "claim_number": "CN-2026-00001",
    "incident_date": "2025-09-14",
    "reported_date": "2025-09-15",
    "claim_type": "Rear-end Collision",
    "incident_location": "Main St & 4th Ave",
    "incident_state": "TX",
    "claimed_amount": 18200.00,
    "paid_amount": 16500.00,
    "deductible_paid": 500.00,
    "claim_status": "Open",
    "subrogation_status": "Demand Ready",
    "description": "Rear-end impact at intersection."
  }
]
```

---

### 1.2 `GET /claims/{claim_id}`
Retrieve complete dossier for an individual claim including policy coverage, customer profile, accident reports, involved parties, documents, and assessments.

**Sample Response (`200 OK`):**
```json
{
  "claim": { "claim_id": "CLM-0001", "paid_amount": 16500.0, "incident_state": "TX" },
  "policy": { "policy_number": "PA-5891230", "coverage_limit": 100000.0, "deductible_amount": 500.0 },
  "customer": { "first_name": "James", "last_name": "Smith", "risk_profile": "Standard" },
  "accident_report": { "police_report_number": "PD-2025-99120", "citations_issued": "Sec 545.062 Following Too Closely" },
  "parties": [
    { "party_type": "Insured Driver", "full_name": "James Smith", "estimated_fault_percentage": 0.0 },
    { "party_type": "Adverse Driver", "full_name": "Robert Taylor", "insurance_carrier": "State Farm", "estimated_fault_percentage": 100.0 }
  ],
  "documents": [
    { "document_name": "police_crash_report.pdf", "is_verified": true }
  ],
  "assessment": {
    "priority_level": "High",
    "net_recovery_estimate": 15675.0,
    "status": "Pending Review"
  }
}
```

---

### 1.3 `POST /claims`
Registers a new insurance claim file into the system.

**Request Payload:**
```json
{
  "policy_id": "POL-0001",
  "customer_id": "CUST-0001",
  "claim_number": "CN-2026-99001",
  "incident_date": "2026-01-15",
  "reported_date": "2026-01-16",
  "claim_type": "Rear-end Collision",
  "incident_location": "I-35 North & 12th St",
  "incident_state": "TX",
  "claimed_amount": 24000.0,
  "paid_amount": 21500.0,
  "deductible_paid": 500.0,
  "description": "Stopped vehicle struck in rear by adverse commercial van."
}
```

---

## 2. Document & Evidence Ingestion Endpoints

### 2.1 `POST /claims/{claim_id}/documents`
Uploads a PDF claim document (e.g. Police Report, Repair Estimate, Witness Statement), extracts text using PyPDF, chunks text semantically, indexes into ChromaDB vector store, and registers database metadata.

**Form Data:**
- `file` (binary PDF, max 15MB)
- `document_type` (string, e.g. `Police Crash Report`)
- `is_verified` (boolean, default=true)

---

## 3. Multi-Agent Investigation & Governance Endpoints

### 3.1 `POST /claims/{claim_id}/investigate`
Triggers the full 6-agent LangGraph orchestration pipeline for a specific claim.

**Sample Response (`200 OK`):**
```json
{
  "status": "COMPLETED",
  "claim_id": "CLM-0001",
  "priority_level": "High",
  "priority_score": 0.9683,
  "adverse_fault_pct": 80.0,
  "net_recovery_estimate": 34970.64,
  "insured_deductible_recovery": 200.00,
  "executive_summary": "Subrogation investigation for claim CLM-0001 concluded an estimated 80.0% potential liability against the adverse party...",
  "recommended_actions": [
    "Issue formal Subrogation Demand Package within 5 business days.",
    "Submit proof-of-loss ledger and certified repair invoice."
  ],
  "agent_logs_count": 6
}
```

---

### 3.2 `GET /claims/{claim_id}/assessment`
Retrieves existing assessment outputs and full chronological execution traces for the claim.

---

### 3.3 `POST /claims/{claim_id}/review`
Records an authorized human adjuster's governance sign-off or adjustment (Human-in-the-Loop checkpoint).

**Request Payload:**
```json
{
  "reviewer_name": "Senior Claims Specialist",
  "reviewer_role": "Lead Subrogation Adjuster",
  "decision": "Approved",
  "adjusted_fault_pct": 80.0,
  "adjusted_net_recovery": 34970.64,
  "review_notes": "Police report and citation verify clear liability. Approved for immediate demand dispatch."
}
```

---

## 4. Reports & PDF Export Endpoints

### 4.1 `GET /reports`
Lists all generated formal investigation reports.

### 4.2 `GET /reports/{report_id}`
Retrieves full 14-section report JSON dossier.

### 4.3 `GET /reports/{report_id}/download`
Streams and downloads the compiled, court-ready ReportLab investigation PDF report.

---

## 5. Analytics & Telemetry Endpoints

### 5.1 `GET /analytics/overview`
Returns portfolio recovery analytics, total paid exposures, projected net recovery, and priority distributions.

### 5.2 `GET /pipeline/status`
Returns ETL execution history, records processed, duration, and data quality constraint audit scores.

### 5.3 `POST /pipeline/run`
Triggers on-demand execution of the complete Data Engineering ETL pipeline.

### 5.4 `GET /model/metrics`
Returns trained Random Forest classifier metrics, test set accuracy, ROC-AUC, confusion matrix, and feature importances.

### 5.5 `GET /health`
Probes database connectivity and returns operational health status.
