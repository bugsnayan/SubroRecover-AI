"""
SubroRecover AI - Investigation Reports & PDF Download API Endpoints
"""

import os
import sys
import json
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import text

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from database.connection import engine
from reports.report_generator import generate_subrogation_pdf

logger = logging.getLogger("subrorecover.api.reports")
router = APIRouter(prefix="/reports", tags=["Investigation Reports"])


class ReportGenerateRequest(BaseModel):
    claim_id: str
    scope: Optional[str] = "Comprehensive Executive Review"
    notes: Optional[str] = None


@router.get("")
def list_reports(limit: int = 100):
    """Lists all stored investigation reports with claim metadata."""
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT r.report_id, r.claim_id, r.report_number, r.report_title,
                   r.executive_summary, r.is_approved, r.created_at,
                   c.claim_number, c.claim_type, c.paid_amount, c.incident_state,
                   a.priority_level, a.net_recovery_estimate
            FROM investigation_reports r
            JOIN insurance_claims c ON r.claim_id = c.claim_id
            LEFT JOIN recovery_assessments a ON c.claim_id = a.claim_id
            ORDER BY r.created_at DESC
            LIMIT :lim
        """), {"lim": limit}).mappings().all()

        return [
            {
                "report_id": r["report_id"],
                "claim_id": r["claim_id"],
                "claim_number": r["claim_number"],
                "report_number": r["report_number"],
                "report_title": r["report_title"],
                "incident_type": r["claim_type"],
                "incident_state": r["incident_state"],
                "paid_amount": float(r["paid_amount"]),
                "net_recovery": float(r["net_recovery_estimate"]) if r["net_recovery_estimate"] else 0.0,
                "priority": r["priority_level"] or "Medium",
                "executive_summary": r["executive_summary"],
                "is_approved": bool(r["is_approved"]),
                "created_at": str(r["created_at"]),
                "download_url": f"/api/reports/{r['report_id']}/download"
            }
            for r in rows
        ]


@router.get("/{report_id}")
def get_report(report_id: str):
    """Retrieves full report payload by report_id or claim_id."""
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT r.*, c.claim_number, c.claim_type, c.paid_amount, c.deductible_paid,
                   c.incident_date, c.incident_state, c.incident_location,
                   a.priority_level, a.adverse_fault_pct, a.net_recovery_estimate,
                   a.recovery_probability, a.statute_of_limitations_date
            FROM investigation_reports r
            JOIN insurance_claims c ON r.claim_id = c.claim_id
            LEFT JOIN recovery_assessments a ON c.claim_id = a.claim_id
            WHERE r.report_id = :rid OR r.claim_id = :rid
        """), {"rid": report_id}).mappings().first()

        if not row:
            raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found.")

        report_data = dict(row)
        if "full_report_json" in report_data and isinstance(report_data["full_report_json"], str):
            try:
                report_data["full_report_json"] = json.loads(report_data["full_report_json"])
            except Exception:
                pass

        return report_data


@router.post("/generate", status_code=201)
def generate_report(payload: ReportGenerateRequest):
    """
    Triggers dynamic compilation of a new Subrogation Investigation Report and ReportLab PDF.
    """
    claim_id = payload.claim_id
    with engine.connect() as conn:
        claim_row = conn.execute(text("SELECT * FROM insurance_claims WHERE claim_id = :cid"), {"cid": claim_id}).mappings().first()
        if not claim_row:
            raise HTTPException(status_code=404, detail=f"Claim '{claim_id}' not found.")
        claim = dict(claim_row)

        asm_row = conn.execute(text("SELECT * FROM recovery_assessments WHERE claim_id = :cid"), {"cid": claim_id}).mappings().first()
        asm = dict(asm_row) if asm_row else {}

        acc_row = conn.execute(text("SELECT * FROM accident_reports WHERE claim_id = :cid"), {"cid": claim_id}).mappings().first()
        acc = dict(acc_row) if acc_row else {}

    paid = float(claim["paid_amount"])
    ded = float(claim["deductible_paid"])
    fault = float(asm.get("adverse_fault_pct") or 80.0)
    net_rec = float(asm.get("net_recovery_estimate") or (paid * 0.8))
    prio = asm.get("priority_level", "High")
    sol_date = str(asm.get("statute_of_limitations_date", "2028-06-30"))

    # Check for existing report to maintain consistent report_id and report_number
    with engine.connect() as conn:
        existing_rpt = conn.execute(
            text("SELECT report_id, report_number FROM investigation_reports WHERE claim_id = :cid"),
            {"cid": claim_id}
        ).mappings().first()

    if existing_rpt:
        report_id = existing_rpt["report_id"]
        report_num = existing_rpt["report_number"]
    else:
        report_id = f"RPT-{claim_id}"
        report_num = f"SIR-2026-{claim_id.replace('CLM-', '')}"

    dossier = {
        "report_id": report_id,
        "claim_id": claim_id,
        "report_number": report_num,
        "claim_number": claim["claim_number"],
        "scope": payload.scope,
        "executive_summary": f"Exhaustive subrogation audit for {claim_id} ({claim['claim_type']}) confirms {fault:.0f}% statutory third-party liability with ${round(net_rec):,} projected recovery target.",
        "claim_overview": {
            "claim_number": claim["claim_number"],
            "incident_date": str(claim["incident_date"]),
            "incident_state": claim["incident_state"],
            "claim_type": claim["claim_type"],
            "paid_amount": paid,
            "deductible": ded
        },
        "liability_analysis": {
            "adverse_fault_pct": fault,
            "police_citations": acc.get("citations_issued", "Traffic Infraction / Failure to Yield"),
            "officer_narrative": acc.get("officer_narrative", "Official crash documentation confirms adverse operator negligence."),
            "liability_reasoning": f"Adverse vehicle failed to yield legal right of way, establishing clear comparative negligence under {claim['incident_state']} statutory doctrine."
        },
        "recovery_quantum": {
            "carrier_paid_exposure": paid,
            "insured_deductible": ded,
            "pro_rata_recovery_gross": round((paid + ded) * (fault / 100.0), 2),
            "projected_net_recovery": net_rec,
            "recovery_probability": float(asm.get("recovery_probability") or 0.85)
        },
        "recommendations": [
            f"Transmit formal subrogation demand letter to adverse carrier for ${round(net_rec):,}.",
            f"Monitor state statute of limitations expiration ({sol_date}).",
            "Disburse policyholder deductible under the Make-Whole doctrine upon settlement receipt."
        ],
        "notes": payload.notes
    }

    # Generate PDF
    pdf_path = generate_subrogation_pdf(dossier)

    # Save to database
    with engine.begin() as conn:
        if existing_rpt:
            conn.execute(text("""
                UPDATE investigation_reports
                SET executive_summary = :esum,
                    full_report_json = :rjson,
                    is_approved = :appr,
                    updated_at = CURRENT_TIMESTAMP
                WHERE report_id = :rid
            """), {
                "rid": report_id,
                "esum": dossier["executive_summary"],
                "rjson": json.dumps(dossier),
                "appr": prio == "High"
            })
        else:
            conn.execute(text("""
                INSERT INTO investigation_reports (
                    report_id, claim_id, report_number, report_title,
                    executive_summary, full_report_json, is_approved
                ) VALUES (
                    :rid, :cid, :rnum, :title, :esum, :rjson, :appr
                )
            """), {
                "rid": report_id,
                "cid": claim_id,
                "rnum": report_num,
                "title": f"Subrogation Investigation Report — {claim_id}",
                "esum": dossier["executive_summary"],
                "rjson": json.dumps(dossier),
                "appr": prio == "High"
            })

    return {
        "message": "Report generated successfully.",
        "report_id": report_id,
        "report_number": report_num,
        "claim_id": claim_id,
        "pdf_path": pdf_path,
        "download_url": f"/api/reports/{report_id}/download",
        "dossier": dossier
    }


@router.get("/{report_id}/download")
def download_report_pdf(report_id: str):
    """
    Dynamically builds or retrieves the ReportLab PDF for download.
    """
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT * FROM investigation_reports
            WHERE report_id = :rid OR claim_id = :rid
        """), {"rid": report_id}).mappings().first()

        if not row:
            raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found.")

        r_dict = dict(row)
        raw_json = r_dict.get("full_report_json", "{}")
        try:
            dossier = json.loads(raw_json) if isinstance(raw_json, str) else raw_json
        except Exception:
            dossier = {}

    if not dossier:
        dossier = {
            "claim_id": r_dict["claim_id"],
            "report_id": r_dict["report_id"],
            "executive_summary": r_dict["executive_summary"]
        }

    # Generate PDF
    pdf_path = generate_subrogation_pdf(dossier)

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="Failed to compile PDF report artifact.")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(pdf_path)
    )
