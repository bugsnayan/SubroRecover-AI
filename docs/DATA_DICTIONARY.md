# SubroRecover AI — Enterprise Data Dictionary

## 1. Schema Overview

The relational database architecture is designed for ANSI SQL compliance, providing primary production deployment on PostgreSQL 15+ and automatic zero-configuration fallback to SQLite 3.35+.

---

## 2. Table Specifications

### 2.1 `customers`
Stores policyholder identity and risk rating profiles.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `customer_id` | VARCHAR(50) | PRIMARY KEY | Unique customer identifier (e.g., `CUST-0001`) |
| `first_name` | VARCHAR(100) | NOT NULL | Customer first name |
| `last_name` | VARCHAR(100) | NOT NULL | Customer surname |
| `email` | VARCHAR(150) | NOT NULL | Policyholder contact email |
| `phone` | VARCHAR(30) | NULLABLE | Primary contact phone number |
| `address` | VARCHAR(255) | NULLABLE | Street address |
| `city` | VARCHAR(100) | NULLABLE | City of residence |
| `state` | VARCHAR(50) | NULLABLE | State jurisdiction (e.g., `TX`, `CA`) |
| `postal_code` | VARCHAR(20) | NULLABLE | Postal / ZIP code |
| `risk_profile` | VARCHAR(50) | DEFAULT 'Standard' | Underwriting tier: `Preferred`, `Standard`, `Non-Standard` |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Ingestion timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Modification timestamp |

---

### 2.2 `insurance_policies`
Tracks coverage limits, deductible thresholds, and policy effective windows.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `policy_id` | VARCHAR(50) | PRIMARY KEY | Unique policy key (e.g., `POL-0001`) |
| `customer_id` | VARCHAR(50) | NOT NULL, FK(`customers`) | References owning customer |
| `policy_number` | VARCHAR(100) | UNIQUE, NOT NULL | Policy certificate number |
| `policy_type` | VARCHAR(50) | NOT NULL | `Personal Auto`, `Commercial Auto`, `Fleet Vehicle` |
| `coverage_limit` | NUMERIC(12, 2) | NOT NULL, CHECK > 0 | Maximum policy benefit cap |
| `deductible_amount` | NUMERIC(10, 2) | NOT NULL, CHECK >= 0 | Policyholder deductible liability |
| `effective_date` | DATE | NOT NULL | Policy inception date |
| `expiration_date` | DATE | NOT NULL | Policy renewal / expiration date |
| `status` | VARCHAR(30) | DEFAULT 'Active' | `Active`, `Expired`, `Cancelled` |

---

### 2.3 `insurance_claims`
Core operational claims table tracking reported loss, carrier disbursements, and recovery status.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `claim_id` | VARCHAR(50) | PRIMARY KEY | Unique claim key (e.g., `CLM-0001`) |
| `policy_id` | VARCHAR(50) | NOT NULL, FK(`insurance_policies`) | References linked policy |
| `customer_id` | VARCHAR(50) | NOT NULL, FK(`customers`) | References policyholder |
| `claim_number` | VARCHAR(100) | UNIQUE, NOT NULL | External carrier claim identifier |
| `incident_date` | DATE | NOT NULL | Date loss occurred |
| `reported_date` | DATE | NOT NULL | Date first notice of loss (FNOL) filed |
| `claim_type` | VARCHAR(50) | NOT NULL | Accident classification (e.g., `Rear-end Collision`) |
| `incident_location`| VARCHAR(255) | NULLABLE | Intersection or highway location |
| `incident_state` | VARCHAR(50) | NOT NULL | State code governing comparative negligence |
| `claimed_amount` | NUMERIC(12, 2) | NOT NULL | Gross claimed damages amount |
| `paid_amount` | NUMERIC(12, 2) | NOT NULL, CHECK >= 0 | Actual net disbursement paid by carrier |
| `deductible_paid` | NUMERIC(10, 2) | DEFAULT 0.0 | Out-of-pocket deductible paid by insured |
| `claim_status` | VARCHAR(50) | DEFAULT 'Open' | `Open`, `In Review`, `Under Investigation`, `Settled` |
| `subrogation_status`| VARCHAR(50) | DEFAULT 'Identified' | `Identified`, `Demand Ready`, `In Triage`, `Closed No Subro` |
| `description` | TEXT | NULLABLE | Loss circumstances statement |

---

### 2.4 `accident_reports`
Contains official police accident report findings, citations, and collision narratives.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `report_id` | VARCHAR(50) | PRIMARY KEY | Unique accident report identifier |
| `claim_id` | VARCHAR(50) | NOT NULL, FK(`insurance_claims`) | References associated claim |
| `police_report_number`| VARCHAR(100)| NULLABLE | Municipal / state police incident number |
| `reporting_officer`| VARCHAR(100)| NULLABLE | Officer name and badge ID |
| `police_department`| VARCHAR(150)| NULLABLE | Responding law enforcement agency |
| `weather_conditions`| VARCHAR(100)| NULLABLE | Weather factors (e.g., `Clear / Dry`, `Rain / Wet`) |
| `road_conditions` | VARCHAR(100)| NULLABLE | Surface type (e.g., `Dry Asphalt`, `Intersection`) |
| `officer_narrative`| TEXT | NULLABLE | Detailed police investigation narrative |
| `citations_issued` | TEXT | NULLABLE | Statutory traffic violations cited |
| `primary_contributing_factor`| VARCHAR(200)| NULLABLE | Primary collision cause identified by officer |
| `points_of_impact`| VARCHAR(200)| NULLABLE | Damaged vehicle sectors |
| `diagram_available`| BOOLEAN | DEFAULT FALSE | Whether accident reconstruction diagram exists |

---

### 2.5 `involved_parties`
Tracks first-party insured, adverse operators, claimants, and adverse insurance carriers.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `party_id` | VARCHAR(50) | PRIMARY KEY | Unique party identifier |
| `claim_id` | VARCHAR(50) | NOT NULL, FK(`insurance_claims`) | Associated claim |
| `party_type` | VARCHAR(50) | NOT NULL | `Insured Driver`, `Adverse Driver`, `Witness` |
| `full_name` | VARCHAR(150)| NOT NULL | Driver or entity name |
| `vehicle_year_make_model`| VARCHAR(150)| NULLABLE | Vehicle specification |
| `license_plate` | VARCHAR(50) | NULLABLE | Vehicle registration number |
| `insurance_carrier`| VARCHAR(150)| NULLABLE | Adverse insurer (e.g., `GEICO`, `State Farm`) |
| `estimated_fault_percentage`| NUMERIC(5, 2)| DEFAULT 0.0 | Preliminary fault allocation (0 to 100%) |
| `citation_received`| BOOLEAN | DEFAULT FALSE | Whether party was cited by law enforcement |
| `statement_summary`| TEXT | NULLABLE | Summary of party statements recorded |

---

### 2.6 `recovery_assessments`
Stores multi-agent reasoning outputs, predictive ML priority tiers, and Make-Whole calculations.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `assessment_id` | VARCHAR(50) | PRIMARY KEY | Assessment key (e.g., `ASM-CLM-0001`) |
| `claim_id` | VARCHAR(50) | NOT NULL, FK(`insurance_claims`) | Claim dossier assessed |
| `priority_level` | VARCHAR(20) | NOT NULL | Triage urgency: `High`, `Medium`, `Low` |
| `priority_score` | NUMERIC(5, 4) | NOT NULL | ML model confidence score (0.0000 - 1.0000) |
| `estimated_adverse_fault_pct`| NUMERIC(5, 2)| NOT NULL | Assessed adverse comparative liability % |
| `gross_recovery_estimate`| NUMERIC(12, 2)| NOT NULL | Theoretical full third-party liability exposure |
| `net_recovery_estimate`| NUMERIC(12, 2)| NOT NULL | Projected net recovery after Make-Whole & costs |
| `insured_deductible_recovery`| NUMERIC(10, 2)| DEFAULT 0.0 | Make-Whole deductible refund owed to insured |
| `liability_rationale`| TEXT | NULLABLE | Legal doctrine and negligence reasoning |
| `quantum_rationale`| TEXT | NULLABLE | Accounting methodology and limitation assumptions |
| `missing_evidence`| TEXT | NULLABLE | Evidentiary gaps flagged for adjuster follow-up |
| `status` | VARCHAR(50) | DEFAULT 'Pending Review' | Governance state: `Pending Review`, `Adjuster Approved` |

---

### 2.7 `agent_execution_logs`
Chronological execution audit trail recording every agent step, input, duration, and output.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `log_id` | VARCHAR(50) | PRIMARY KEY | Unique execution trace ID |
| `claim_id` | VARCHAR(50) | NOT NULL, FK(`insurance_claims`) | Claim being investigated |
| `agent_name` | VARCHAR(100)| NOT NULL | Agent module (e.g., `Claim Analysis Agent`) |
| `execution_step` | INTEGER | NOT NULL | Workflow step sequence (1 through 6) |
| `status` | VARCHAR(50) | NOT NULL | `Running`, `Completed`, `Failed` |
| `input_payload` | TEXT | NULLABLE | Summary of inputs provided to agent |
| `output_payload` | TEXT | NULLABLE | Structured findings emitted by agent |
| `execution_duration_ms`| INTEGER | NOT NULL | Execution runtime in milliseconds |

---

### 2.8 `investigation_reports`
Synthesized investigation dossiers prepared for adjuster sign-off and formal PDF generation.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `report_id` | VARCHAR(50) | PRIMARY KEY | Unique report key (e.g., `RPT-CLM-0001`) |
| `claim_id` | VARCHAR(50) | NOT NULL, FK(`insurance_claims`) | Claim investigated |
| `report_number` | VARCHAR(100)| UNIQUE, NOT NULL | Official formal report identifier |
| `executive_summary`| TEXT | NOT NULL | High-level findings synthesis |
| `full_report_json`| TEXT | NOT NULL | Complete 14-section JSON dossier |
| `is_approved` | BOOLEAN | DEFAULT FALSE | Human adjuster authorization flag |

---

### 2.9 `human_review_records`
Audit table recording all Human-in-the-Loop adjuster review decisions and modifications.

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `review_id` | VARCHAR(50) | PRIMARY KEY | Unique review transaction ID |
| `claim_id` | VARCHAR(50) | NOT NULL, FK(`insurance_claims`) | Claim under review |
| `reviewer_name` | VARCHAR(100)| NOT NULL | Authorized adjuster name |
| `reviewer_role` | VARCHAR(100)| NOT NULL | Adjuster organizational title |
| `decision` | VARCHAR(50) | NOT NULL | `Approved`, `Modified`, `Rejected`, `Escalate` |
| `adjusted_fault_pct`| NUMERIC(5, 2)| NULLABLE | Human override of adverse liability % |
| `review_notes` | TEXT | NULLABLE | Justification notes entered by adjuster |
| `reviewed_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Review decision timestamp |
