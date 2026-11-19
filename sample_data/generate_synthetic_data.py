"""
SubroRecover AI - Synthetic Insurance Data Generator
Generates realistic, domain-accurate datasets for insurance claims,
policies, accident narratives, parties, and historical recoveries.
"""

import os
import random
import datetime
import pandas as pd
import numpy as np

def generate_datasets(num_customers=120, num_claims=180, seed=42):
    random.seed(seed)
    np.random.seed(seed)

    os.makedirs("sample_data", exist_ok=True)

    # 1. Customers
    first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
                   "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
                   "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
                   "Matthew", "Margaret", "Anthony", "Betty", "Mark", "Sandra", "Donald", "Ashley"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                  "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
                  "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White"]
    cities_states = [
        ("Dallas", "TX", "75201"), ("Houston", "TX", "77002"), ("Austin", "TX", "78701"),
        ("Los Angeles", "CA", "90012"), ("San Francisco", "CA", "94102"), ("San Diego", "CA", "92101"),
        ("Miami", "FL", "33101"), ("Orlando", "FL", "32801"), ("Tampa", "FL", "33602"),
        ("Chicago", "IL", "60601"), ("Naperville", "IL", "60540"), ("Peoria", "IL", "61602"),
        ("Phoenix", "AZ", "85001"), ("Tucson", "AZ", "85701"), ("Scottsdale", "AZ", "85251"),
        ("Atlanta", "GA", "30301"), ("Savannah", "GA", "31401"), ("Columbus", "OH", "43215")
    ]
    risk_profiles = ["Preferred", "Standard", "Non-Standard", "Commercial"]

    customers = []
    for i in range(1, num_customers + 1):
        cid = f"CUST-{i:04d}"
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        city, state, zip_code = random.choice(cities_states)
        email = f"{fn.lower()}.{ln.lower()}{random.randint(10,99)}@example.com"
        phone = f"+1-{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}"
        addr = f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Maple', 'Cedar', 'Elm', 'Pine', 'Washington', 'Park'])} St"
        risk = random.choices(risk_profiles, weights=[0.4, 0.45, 0.1, 0.05])[0]
        customers.append({
            "customer_id": cid,
            "first_name": fn,
            "last_name": ln,
            "email": email,
            "phone": phone,
            "address": addr,
            "city": city,
            "state": state,
            "postal_code": zip_code,
            "risk_profile": risk
        })
    df_customers = pd.DataFrame(customers)
    df_customers.to_csv("sample_data/customers.csv", index=False)

    # 2. Insurance Policies
    policy_types = ["Personal Auto", "Commercial Auto", "Fleet Vehicle", "Comprehensive Property"]
    policies = []
    for i in range(1, num_customers + 1):
        pid = f"POL-{i:04d}"
        cid = f"CUST-{i:04d}"
        p_num = f"PA-{random.randint(1000000, 9999999)}"
        ptype = random.choices(policy_types, weights=[0.7, 0.2, 0.05, 0.05])[0]
        limit = random.choice([50000.0, 100000.0, 250000.0, 500000.0, 1000000.0])
        deductible = random.choice([250.0, 500.0, 1000.0, 1500.0, 2000.0])
        eff_date = datetime.date(2025, random.randint(1, 6), random.randint(1, 28))
        exp_date = eff_date + datetime.timedelta(days=365)
        policies.append({
            "policy_id": pid,
            "customer_id": cid,
            "policy_number": p_num,
            "policy_type": ptype,
            "coverage_limit": limit,
            "deductible_amount": deductible,
            "effective_date": eff_date.isoformat(),
            "expiration_date": exp_date.isoformat(),
            "status": "Active"
        })
    df_policies = pd.DataFrame(policies)
    df_policies.to_csv("sample_data/policies.csv", index=False)

    # 3. Insurance Claims
    claim_scenarios = [
        ("Rear-end Collision", "Adverse driver failed to stop at red signal and rear-ended insured vehicle at intersection.", 0.95, "Adverse Party"),
        ("Failure to Yield", "Adverse driver made an unprotected left turn across oncoming traffic, colliding with insured front bumper.", 0.90, "Adverse Party"),
        ("Side-swipe Lane Change", "Adverse vehicle changed lanes improperly without signaling, striking insured right quarter panel.", 0.85, "Adverse Party"),
        ("T-bone Intersection Impact", "Adverse driver disregarded red light and impacted driver side of insured vehicle.", 0.95, "Adverse Party"),
        ("Backing from Driveway", "Adverse vehicle backed out of private driveway directly into insured traveling on public roadway.", 0.80, "Adverse Party"),
        ("Single Vehicle Impact", "Insured swerved to avoid debris on roadway and made contact with guardrail.", 0.00, "Insured Only"),
        ("Hit and Run Parked Vehicle", "Insured vehicle struck while legally parked on street; adverse vehicle fled scene.", 0.70, "Unidentified Adverse"),
        ("Multi-Vehicle Chain Collision", "Adverse commercial truck failed to brake in stop-and-go traffic, creating a 3-car pileup.", 0.90, "Adverse Party")
    ]

    claims = []
    accident_reports = []
    involved_parties = []
    evidence_docs = []
    historical_recoveries = []

    adverse_carriers = [
        "State Farm Insurance", "GEICO General", "Progressive Casualty",
        "Allstate Indemnity", "Travelers Commercial", "Liberty Mutual",
        "Nationwide Mutual", "American Family"
    ]

    vehicles = [
        "2022 Toyota Camry", "2021 Honda Accord", "2023 Ford F-150",
        "2020 Chevrolet Silverado", "2024 Tesla Model 3", "2019 Nissan Altima",
        "2022 Hyundai Tucson", "2023 Subaru Outback", "2021 Jeep Grand Cherokee",
        "2020 Freightliner Cascadia"
    ]

    for i in range(1, num_claims + 1):
        claim_id = f"CLM-{i:04d}"
        cust_idx = (i - 1) % num_customers + 1
        cid = f"CUST-{cust_idx:04d}"
        pid = f"POL-{cust_idx:04d}"
        policy = df_policies.iloc[cust_idx - 1]
        deductible = float(policy["deductible_amount"])

        scenario_name, base_narrative, subro_prob, fault_type = random.choice(claim_scenarios)
        
        # Incident dates between mid 2025 and 2026
        inc_date = datetime.date(2025, random.randint(7, 12), random.randint(1, 28))
        rep_delay = random.choices([0, 1, 2, 3, 5, 10, 20], weights=[0.4, 0.3, 0.15, 0.08, 0.04, 0.02, 0.01])[0]
        rep_date = inc_date + datetime.timedelta(days=rep_delay)

        # Financials
        paid_amt = round(random.uniform(2500.0, 48000.0), 2)
        claimed_amt = round(paid_amt + deductible + random.uniform(200.0, 1500.0), 2)
        
        status = random.choices(["Open", "Under Investigation", "In Review", "Settled"], weights=[0.4, 0.35, 0.15, 0.1])[0]
        subro_status = "Identified" if subro_prob > 0.6 else ("Closed No Subro" if subro_prob == 0 else "In Triage")

        city, state, _ = random.choice(cities_states)
        loc = f"{random.randint(100, 5000)} {random.choice(['Westheimer Rd', 'I-35 North', 'Sunset Blvd', 'Biscayne Blvd', 'Michigan Ave', 'Peachtree St', 'Camelback Rd'])}"

        claims.append({
            "claim_id": claim_id,
            "policy_id": pid,
            "customer_id": cid,
            "claim_number": f"CN-2026-{i:05d}",
            "incident_date": inc_date.isoformat(),
            "reported_date": rep_date.isoformat(),
            "claim_type": scenario_name,
            "incident_location": loc,
            "incident_state": state,
            "claimed_amount": claimed_amt,
            "paid_amount": paid_amt,
            "deductible_paid": deductible,
            "claim_status": status,
            "subrogation_status": subro_status,
            "description": f"{scenario_name} at {loc}, {city}, {state}. {base_narrative}"
        })

        # 4. Accident Report
        rep_id = f"REP-{i:04d}"
        has_police = (fault_type != "Single Vehicle Impact" and random.random() > 0.1)
        officer = f"Officer {random.choice(last_names)} #{random.randint(1000, 9999)}"
        dept = f"{city} Police Department - Traffic Division"
        
        adverse_citations = []
        if subro_prob >= 0.8:
            adverse_citations = random.choices([
                "Failure to Control Speed (Sec 545.351)",
                "Disregard Red Traffic Signal (Sec 544.007)",
                "Failure to Yield Right of Way at Left Turn (Sec 545.152)",
                "Improper Lane Change (Sec 545.060)",
                "Following Too Closely (Sec 545.062)"
            ], k=random.randint(1, 2))

        narrative = (
            f"On {inc_date.isoformat()}, officer responded to a {scenario_name.lower()} at {loc}. "
            f"Unit 1 (Insured) was traveling through roadway when Unit 2 (Adverse) {base_narrative.lower()} "
            f"{'Citations issued to Unit 2: ' + ', '.join(adverse_citations) if adverse_citations else 'No field citations noted.'} "
            f"Both vehicles sustained disabling damage. Statements obtained from both operators on scene."
        ) if has_police else "No official police crash report filed on date of incident. Operator self-reported incident details."

        accident_reports.append({
            "report_id": rep_id,
            "claim_id": claim_id,
            "police_report_number": f"PD-{inc_date.year}-{random.randint(100000, 999999)}" if has_police else "N/A",
            "reporting_officer": officer if has_police else "N/A",
            "police_department": dept if has_police else "N/A",
            "incident_date": inc_date.isoformat(),
            "weather_conditions": random.choice(["Clear / Dry", "Rain / Wet Roadway", "Cloudy", "Fog / Reduced Visibility", "Snow / Icy"]),
            "road_conditions": random.choice(["Dry Asphalt", "Wet Asphalt", "Concrete Highway", "Intersection with Signals"]),
            "officer_narrative": narrative,
            "citations_issued": "; ".join(adverse_citations) if adverse_citations else "None",
            "primary_contributing_factor": adverse_citations[0] if adverse_citations else "Driver Inattention / Unknown",
            "points_of_impact": random.choice(["Rear End / Front Bumper", "Driver Side T-Bone", "Passenger Quarter Panel", "Frontal Collision"]),
            "diagram_available": has_police
        })

        # 5. Involved Parties
        # Party 1: Insured
        party1_id = f"PTY-{i:04d}-1"
        cust = df_customers.iloc[cust_idx - 1]
        involved_parties.append({
            "party_id": party1_id,
            "claim_id": claim_id,
            "party_type": "Insured Driver",
            "full_name": f"{cust['first_name']} {cust['last_name']}",
            "vehicle_year_make_model": random.choice(vehicles[:5]),
            "license_plate": f"{state}-{random.randint(100, 999)}-{random.choice(['ABC', 'XYZ', 'TRK', 'EXP'])}",
            "driver_license_state": state,
            "insurance_carrier": "SubroRecover Carrier (First-Party)",
            "insurance_policy_number": policy["policy_number"],
            "insurance_claim_number": f"CN-2026-{i:05d}",
            "estimated_fault_percentage": round(100.0 * (1.0 - subro_prob), 2),
            "citation_received": False,
            "statement_summary": "Insured stated they were operating lawfully with right of way when other vehicle caused collision."
        })

        # Party 2: Adverse Driver (if applicable)
        if fault_type != "Insured Only":
            party2_id = f"PTY-{i:04d}-2"
            adv_fn = random.choice(first_names)
            adv_ln = random.choice(last_names)
            adv_carrier = random.choice(adverse_carriers)
            involved_parties.append({
                "party_id": party2_id,
                "claim_id": claim_id,
                "party_type": "Adverse Driver",
                "full_name": f"{adv_fn} {adv_ln}",
                "vehicle_year_make_model": random.choice(vehicles[5:]),
                "license_plate": f"{state}-{random.randint(100, 999)}-{random.choice(['DFG', 'LMN', 'QRS', 'WXY'])}",
                "driver_license_state": state,
                "insurance_carrier": adv_carrier,
                "insurance_policy_number": f"ADV-{random.randint(1000000, 9999999)}",
                "insurance_claim_number": f"ADV-CLM-{random.randint(100000, 999999)}",
                "estimated_fault_percentage": round(100.0 * subro_prob, 2),
                "citation_received": bool(adverse_citations),
                "statement_summary": f"Adverse driver admitted: '{base_narrative}'" if subro_prob > 0.8 else "Adverse driver disputed fault."
            })

        # 6. Evidence Documents Metadata
        doc_types = [
            ("Police Crash Report", "police_report.pdf", True),
            ("Certified Repair Estimate", "repair_estimate.pdf", True),
            ("Operator Statement Transcript", "insured_statement.pdf", True),
            ("Scene Scene Photography", "damage_photos.pdf", False)
        ]
        for d_idx, (dtype, fname, verified) in enumerate(doc_types):
            doc_id = f"DOC-{i:04d}-{d_idx+1}"
            evidence_docs.append({
                "document_id": doc_id,
                "claim_id": claim_id,
                "document_name": f"{claim_id}_{fname}",
                "document_type": dtype,
                "file_path": f"documents/{claim_id}/{fname}",
                "file_size_bytes": random.randint(120000, 1850000),
                "extracted_text": f"Extracted text content from {dtype} for claim {claim_id}. Officer notes and damage appraisal.",
                "ocr_confidence": round(random.uniform(0.92, 0.99), 2),
                "is_verified": verified,
                "upload_date": rep_date.isoformat()
            })

        # 7. Historical Recovery Record (for ML training)
        # Target variable: priority_level ('High', 'Medium', 'Low')
        adverse_fault = round(100.0 * subro_prob, 2)
        has_citations = int(bool(adverse_citations))
        has_police_int = int(has_police)
        num_parties = 2 if fault_type != "Insured Only" else 1

        # Calculate actual recovery ratio
        if adverse_fault >= 80 and has_police_int:
            priority = "High"
            recovery_amount = round(paid_amt * (adverse_fault / 100.0) * random.uniform(0.85, 1.0), 2)
            recovery_status = "Fully Recovered"
        elif adverse_fault >= 50:
            priority = "Medium"
            recovery_amount = round(paid_amt * (adverse_fault / 100.0) * random.uniform(0.50, 0.85), 2)
            recovery_status = "Partially Recovered"
        else:
            priority = "Low"
            recovery_amount = 0.0
            recovery_status = "Closed No Recovery"

        recovery_rate = round(recovery_amount / paid_amt, 4) if paid_amt > 0 else 0.0

        historical_recoveries.append({
            "claim_id": claim_id,
            "claim_amount": claimed_amt,
            "paid_amount": paid_amt,
            "deductible_amount": deductible,
            "claim_type": scenario_name,
            "incident_state": state,
            "num_parties": num_parties,
            "has_police_report": has_police_int,
            "citations_issued": has_citations,
            "adverse_fault_pct": adverse_fault,
            "days_to_report": rep_delay,
            "recovered_amount": recovery_amount,
            "recovery_rate": recovery_rate,
            "recovery_status": recovery_status,
            "priority_level": priority  # ML Target
        })

    # Save to CSV
    pd.DataFrame(claims).to_csv("sample_data/claims.csv", index=False)
    pd.DataFrame(accident_reports).to_csv("sample_data/accident_reports.csv", index=False)
    pd.DataFrame(involved_parties).to_csv("sample_data/involved_parties.csv", index=False)
    pd.DataFrame(evidence_docs).to_csv("sample_data/evidence_documents.csv", index=False)
    pd.DataFrame(historical_recoveries).to_csv("sample_data/historical_recoveries.csv", index=False)

    print(f"Generated synthetic datasets successfully:")
    print(f" - {len(customers)} Customers")
    print(f" - {len(policies)} Policies")
    print(f" - {len(claims)} Claims")
    print(f" - {len(accident_reports)} Accident Reports")
    print(f" - {len(involved_parties)} Involved Parties")
    print(f" - {len(evidence_docs)} Evidence Document Records")
    print(f" - {len(historical_recoveries)} Historical Recovery Profiles")

if __name__ == "__main__":
    generate_datasets()
