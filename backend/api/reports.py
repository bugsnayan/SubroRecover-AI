"""
SubroRecover AI - Investigation Reports & PDF Download API Endpoints
"""

import os
import sys
import json
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import text

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from database.connection import engine
from reports.report_generator import generate_subrogation_pdf

logger = logging.getLogger("subrorecover.api.reports")
router = APIRouter(prefix="/reports", tags=["Investigation Reports"])

@router.get("")
def list_reports(limit: int = 50):
    """Lists all stored investigation reports."""
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT report_id, claim_id, report_number, report_title, executive_summary, is_approved, created_at FROM investigation_reports ORDER BY created_at DESC LIMIT :lim"), {"lim": limit}).mappings().all()
        return [dict(r) for r in rows]

@router.get("/{report_id}")
def get_report(report_id: str):
    """Retrieves full report payload by report_id or claim_id."""
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT * FROM investigation_reports
            WHERE report_id = :rid OR claim_id = :rid
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

    # Ensure dossier has basic metadata
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
