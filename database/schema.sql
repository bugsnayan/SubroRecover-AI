-- ====================================================================
-- SubroRecover AI — Relational Database Schema
-- Compatible with PostgreSQL 15+ and SQLite 3.35+
-- ====================================================================

-- 1. Customers Table
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(30),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    postal_code VARCHAR(20),
    risk_profile VARCHAR(50) DEFAULT 'Standard',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Insurance Policies Table
CREATE TABLE IF NOT EXISTS insurance_policies (
    policy_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    policy_number VARCHAR(100) UNIQUE NOT NULL,
    policy_type VARCHAR(50) NOT NULL, -- Auto Personal, Commercial Auto, Fleet, Property
    coverage_limit NUMERIC(12, 2) NOT NULL,
    deductible_amount NUMERIC(10, 2) NOT NULL,
    effective_date DATE NOT NULL,
    expiration_date DATE NOT NULL,
    status VARCHAR(30) DEFAULT 'Active', -- Active, Expired, Cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- 3. Insurance Claims Table
CREATE TABLE IF NOT EXISTS insurance_claims (
    claim_id VARCHAR(50) PRIMARY KEY,
    policy_id VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    claim_number VARCHAR(100) UNIQUE NOT NULL,
    incident_date DATE NOT NULL,
    reported_date DATE NOT NULL,
    claim_type VARCHAR(50) NOT NULL, -- Rear-end Collision, T-bone, Side-swipe, Head-on, Property Impact
    incident_location VARCHAR(255),
    incident_state VARCHAR(50) NOT NULL,
    claimed_amount NUMERIC(12, 2) NOT NULL,
    paid_amount NUMERIC(12, 2) NOT NULL,
    deductible_paid NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
    claim_status VARCHAR(50) DEFAULT 'Open', -- Open, In Review, Under Investigation, Settled, Closed
    subrogation_status VARCHAR(50) DEFAULT 'Identified', -- Identified, In Triage, Investigating, Demand Sent, Recovered, Closed No Subro
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (policy_id) REFERENCES insurance_policies(policy_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- 4. Accident Reports Table
CREATE TABLE IF NOT EXISTS accident_reports (
    report_id VARCHAR(50) PRIMARY KEY,
    claim_id VARCHAR(50) NOT NULL,
    police_report_number VARCHAR(100),
    reporting_officer VARCHAR(100),
    police_department VARCHAR(150),
    incident_date DATE NOT NULL,
    weather_conditions VARCHAR(100),
    road_conditions VARCHAR(100),
    officer_narrative TEXT,
    citations_issued TEXT,
    primary_contributing_factor VARCHAR(200),
    points_of_impact VARCHAR(200),
    diagram_available BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (claim_id) REFERENCES insurance_claims(claim_id) ON DELETE CASCADE
);

-- 5. Involved Parties Table
CREATE TABLE IF NOT EXISTS involved_parties (
    party_id VARCHAR(50) PRIMARY KEY,
    claim_id VARCHAR(50) NOT NULL,
    party_type VARCHAR(50) NOT NULL, -- Insured Driver, Adverse Driver, Claimant, Witness, Passenger
    full_name VARCHAR(150) NOT NULL,
    vehicle_year_make_model VARCHAR(150),
    license_plate VARCHAR(50),
    driver_license_state VARCHAR(50),
    insurance_carrier VARCHAR(150),
    insurance_policy_number VARCHAR(100),
    insurance_claim_number VARCHAR(100),
    estimated_fault_percentage NUMERIC(5, 2) DEFAULT 0.0,
    citation_received BOOLEAN DEFAULT FALSE,
    statement_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (claim_id) REFERENCES insurance_claims(claim_id) ON DELETE CASCADE
);

-- 6. Evidence Documents Table
CREATE TABLE IF NOT EXISTS evidence_documents (
    document_id VARCHAR(50) PRIMARY KEY,
    claim_id VARCHAR(50) NOT NULL,
    document_name VARCHAR(255) NOT NULL,
    document_type VARCHAR(50) NOT NULL, -- Police Report, Witness Statement, Repair Estimate, Dashcam Still, Scene Photo, Policy Form
    file_path VARCHAR(500) NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    extracted_text TEXT,
    ocr_confidence NUMERIC(5, 2) DEFAULT 1.0,
    is_verified BOOLEAN DEFAULT FALSE,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (claim_id) REFERENCES insurance_claims(claim_id) ON DELETE CASCADE
);

-- 7. Recovery Assessments Table (Multi-Agent & ML Outputs)
CREATE TABLE IF NOT EXISTS recovery_assessments (
    assessment_id VARCHAR(50) PRIMARY KEY,
    claim_id VARCHAR(50) NOT NULL,
    priority_level VARCHAR(20) NOT NULL, -- High, Medium, Low
    priority_score NUMERIC(5, 4) NOT NULL, -- 0.0000 to 1.0000
    estimated_adverse_fault_pct NUMERIC(5, 2) NOT NULL, -- 0 to 100%
    gross_recovery_estimate NUMERIC(12, 2) NOT NULL,
    net_recovery_estimate NUMERIC(12, 2) NOT NULL,
    insured_deductible_recovery NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
    recovery_probability NUMERIC(5, 4) NOT NULL,
    statute_of_limitations_date DATE,
    liability_rationale TEXT,
    quantum_rationale TEXT,
    missing_evidence TEXT,
    status VARCHAR(50) DEFAULT 'Pending Review', -- Pending Review, Adjuster Approved, Adjuster Modified, Rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (claim_id) REFERENCES insurance_claims(claim_id) ON DELETE CASCADE
);

-- 8. Agent Execution Logs Table
CREATE TABLE IF NOT EXISTS agent_execution_logs (
    log_id VARCHAR(50) PRIMARY KEY,
    claim_id VARCHAR(50) NOT NULL,
    agent_name VARCHAR(100) NOT NULL,
    execution_step INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL, -- Running, Completed, Failed, Skipped
    input_payload TEXT,
    output_payload TEXT,
    execution_duration_ms INTEGER NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (claim_id) REFERENCES insurance_claims(claim_id) ON DELETE CASCADE
);

-- 9. Investigation Reports Table
CREATE TABLE IF NOT EXISTS investigation_reports (
    report_id VARCHAR(50) PRIMARY KEY,
    claim_id VARCHAR(50) NOT NULL,
    report_number VARCHAR(100) UNIQUE NOT NULL,
    report_title VARCHAR(255) NOT NULL,
    executive_summary TEXT NOT NULL,
    full_report_json TEXT NOT NULL,
    pdf_file_path VARCHAR(500),
    generated_by VARCHAR(100) DEFAULT 'SubroRecover Multi-Agent Engine',
    is_approved BOOLEAN DEFAULT FALSE,
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (claim_id) REFERENCES insurance_claims(claim_id) ON DELETE CASCADE
);

-- 10. Human Review Records Table
CREATE TABLE IF NOT EXISTS human_review_records (
    review_id VARCHAR(50) PRIMARY KEY,
    claim_id VARCHAR(50) NOT NULL,
    assessment_id VARCHAR(50),
    reviewer_name VARCHAR(100) NOT NULL,
    reviewer_role VARCHAR(100) NOT NULL, -- Senior Adjuster, Subrogation Specialist, Team Lead
    decision VARCHAR(50) NOT NULL, -- Approved, Modified, Rejected, Escalate to Legal
    adjusted_fault_pct NUMERIC(5, 2),
    adjusted_net_recovery NUMERIC(12, 2),
    review_notes TEXT,
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (claim_id) REFERENCES insurance_claims(claim_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_claims_customer ON insurance_claims(customer_id);
CREATE INDEX IF NOT EXISTS idx_claims_status ON insurance_claims(subrogation_status);
CREATE INDEX IF NOT EXISTS idx_policies_customer ON insurance_policies(customer_id);
CREATE INDEX IF NOT EXISTS idx_reports_claim ON accident_reports(claim_id);
CREATE INDEX IF NOT EXISTS idx_parties_claim ON involved_parties(claim_id);
CREATE INDEX IF NOT EXISTS idx_evidence_claim ON evidence_documents(claim_id);
CREATE INDEX IF NOT EXISTS idx_assessments_claim ON recovery_assessments(claim_id);
CREATE INDEX IF NOT EXISTS idx_assessments_priority ON recovery_assessments(priority_level);
CREATE INDEX IF NOT EXISTS idx_logs_claim ON agent_execution_logs(claim_id);
CREATE INDEX IF NOT EXISTS idx_inv_reports_claim ON investigation_reports(claim_id);
