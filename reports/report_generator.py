"""
SubroRecover AI - Enterprise PDF Report Generator
Generates comprehensive, branded 14-section Subrogation Investigation Reports using ReportLab.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas

logger = logging.getLogger("subrorecover.reports")

REPORTS_OUTPUT_DIR = "generated_reports"

class NumberedCanvas(canvas.Canvas):
    """Custom canvas that calculates total pages and draws running headers and footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "SUBRORECOVER AI — CONFIDENTIAL SUBROGATION INVESTIGATION REPORT")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Running Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_str)
        self.drawString(54, 36, "STRICTLY CONFIDENTIAL — FOR AUTHORIZED CLAIMS & LEGAL PERSONNEL ONLY")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        self.restoreState()

def generate_subrogation_pdf(report_dossier: Dict[str, Any], output_path: str = None) -> str:
    """
    Assembles and compiles the 14-section formal investigation report into a PDF file.
    """
    os.makedirs(REPORTS_OUTPUT_DIR, exist_ok=True)
    claim_id = report_dossier.get("claim_id", "CLAIM")
    report_id = report_dossier.get("report_id", f"RPT-{claim_id}")

    if output_path is None:
        output_path = os.path.join(REPORTS_OUTPUT_DIR, f"{report_id}.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    # Styles
    styles = getSampleStyleSheet()
    
    primary_color = colors.HexColor("#0F172A")    # Deep Navy
    accent_color = colors.HexColor("#1D4ED8")     # Corporate Blue
    slate_muted = colors.HexColor("#475569")      # Muted Slate
    bg_light = colors.HexColor("#F8FAFC")         # Crisp Light Gray
    border_color = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=primary_color,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=accent_color,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B")
    )

    body_bold = ParagraphStyle(
        "BodyDarkBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=primary_color
    )

    alert_style = ParagraphStyle(
        "AlertBox",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155")
    )

    story = []

    # Title Banner
    story.append(Paragraph("SUBRORECOVER AI", title_style))
    story.append(Paragraph("AI-POWERED SUBROGATION RECOVERY INTELLIGENCE DOSSIER", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceBefore=0, spaceAfter=8))

    # Meta Grid
    claim_sum = report_dossier.get("claim_overview", {})
    prio = report_dossier.get("prioritization_metrics", {})
    liab = report_dossier.get("liability_assessment", {})
    rec = report_dossier.get("recovery_financials", {})

    meta_data = [
        [
            Paragraph("<b>Report ID:</b>", body_style), Paragraph(str(report_id), body_style),
            Paragraph("<b>Investigation Date:</b>", body_style), Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M"), body_style)
        ],
        [
            Paragraph("<b>Claim Number:</b>", body_style), Paragraph(str(claim_sum.get("claim_number", claim_id)), body_style),
            Paragraph("<b>Priority Urgency:</b>", body_style), Paragraph(f"<b>{prio.get('priority_level', 'Medium')}</b> ({prio.get('priority_score', 0)*100:.1f}%)", body_style)
        ],
        [
            Paragraph("<b>Policyholder:</b>", body_style), Paragraph(str(claim_sum.get("policy_holder", "Insured")), body_style),
            Paragraph("<b>Policy Limit:</b>", body_style), Paragraph(f"${claim_sum.get('coverage_limit', 0):,.2f}", body_style)
        ],
        [
            Paragraph("<b>Carrier Paid Loss:</b>", body_style), Paragraph(f"${claim_sum.get('paid_loss_amount', 0):,.2f}", body_style),
            Paragraph("<b>Projected Net Recovery:</b>", body_style), Paragraph(f"<b>${rec.get('net_carrier_recovery', 0):,.2f}</b>", body_bold)
        ]
    ]

    t_meta = Table(meta_data, colWidths=[110, 140, 110, 144])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg_light),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Section 1 & 2: Executive Summary & Loss Circumstances
    story.append(Paragraph("1. EXECUTIVE INVESTIGATION SUMMARY", h1_style))
    exec_summary_text = report_dossier.get("executive_summary", "Investigation summary pending.")
    story.append(Paragraph(exec_summary_text, body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("2. INCIDENT CIRCUMSTANCES & LOSS NARRATIVE", h1_style))
    narrative_text = claim_sum.get("claim_narrative", "No narrative available.")
    story.append(Paragraph(narrative_text, body_style))
    story.append(Spacer(1, 8))

    # Section 3: Involved Parties Table
    story.append(Paragraph("3. INVOLVED PARTIES & INSURANCE CARRIERS", h1_style))
    ev_findings = report_dossier.get("evidentiary_findings", {})
    parties_data = [
        [
            Paragraph("<b>Party Role</b>", body_bold),
            Paragraph("<b>Operator / Entity</b>", body_bold),
            Paragraph("<b>Vehicle Details</b>", body_bold),
            Paragraph("<b>Carrier / Insurer</b>", body_bold)
        ],
        [
            Paragraph("First-Party (Insured)", body_style),
            Paragraph(claim_sum.get("policy_holder", "Insured"), body_style),
            Paragraph("Insured Vehicle", body_style),
            Paragraph("SubroRecover Carrier", body_style)
        ],
        [
            Paragraph("Adverse Party", body_style),
            Paragraph(str(ev_findings.get("adverse_party_name", "Adverse Operator")), body_style),
            Paragraph(str(ev_findings.get("adverse_vehicle", "Adverse Vehicle")), body_style),
            Paragraph(str(ev_findings.get("adverse_carrier", "Adverse Insurer")), body_style)
        ]
    ]
    t_parties = Table(parties_data, colWidths=[120, 130, 120, 134])
    t_parties.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_parties)
    story.append(Spacer(1, 8))

    # Section 4: Evidentiary Audit & Verified Facts
    story.append(Paragraph("4. EVIDENTIARY AUDIT & PROVENANCE CITATIONS", h1_style))
    verified_facts = report_dossier.get("verified_facts", [])
    if verified_facts:
        for f in verified_facts[:3]:
            story.append(Paragraph(f"• <b>[VERIFIED FACT]</b> {f}", body_style))
            story.append(Spacer(1, 2))
    else:
        story.append(Paragraph("• No certified external police reports linked to dossier.", body_style))

    citations = report_dossier.get("statutory_citations", [])
    if citations:
        for c in citations:
            story.append(Paragraph(f"• <b>[STATUTORY CITATION]</b> {c}", body_style))
            story.append(Spacer(1, 2))
    story.append(Spacer(1, 6))

    # Section 5 & 6: Liability & Financial Quantum
    story.append(Paragraph("5. COMPARATIVE LIABILITY ASSESSMENT", h1_style))
    liab_text = liab.get("liability_rationale", "Liability rationale pending.")
    story.append(Paragraph(liab_text, body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("6. FINANCIAL RECOVERY QUANTUM (MAKE-WHOLE ALLOCATION)", h1_style))
    fin_data = [
        [Paragraph("<b>Metric</b>", body_bold), Paragraph("<b>Amount (USD)</b>", body_bold), Paragraph("<b>Accounting Description</b>", body_bold)],
        [Paragraph("Total Carrier Paid Loss", body_style), Paragraph(f"${claim_sum.get('paid_loss_amount', 0):,.2f}", body_style), Paragraph("Total disbursements paid out by first-party carrier", body_style)],
        [Paragraph("Insured Deductible Paid", body_style), Paragraph(f"${claim_sum.get('deductible_amount', 0):,.2f}", body_style), Paragraph("Out-of-pocket deductible paid by insured policyholder", body_style)],
        [Paragraph("Adverse Fault Allocation", body_style), Paragraph(f"{liab.get('adverse_fault_pct', 0):.1f}%", body_style), Paragraph(f"Negligence split based on {liab.get('negligence_doctrine', 'Comparative Fault')}", body_style)],
        [Paragraph("Gross Recovery Potential", body_style), Paragraph(f"${rec.get('gross_recovery_estimate', 0):,.2f}", body_style), Paragraph("Theoretical full third-party liability exposure", body_style)],
        [Paragraph("Insured Make-Whole Refund", body_style), Paragraph(f"${rec.get('insured_deductible_recovery', 0):,.2f}", body_style), Paragraph("First-dollar refund returned directly to policyholder", body_style)],
        [Paragraph("Estimated Collection Costs", body_style), Paragraph(f"${rec.get('estimated_collection_cost', 0):,.2f}", body_style), Paragraph("Estimated arbitration and administrative recovery overhead", body_style)],
        [Paragraph("<b>Net Carrier Recovery</b>", body_bold), Paragraph(f"<b>${rec.get('net_carrier_recovery', 0):,.2f}</b>", body_bold), Paragraph("<b>Estimated net carrier recovery yield</b>", body_bold)]
    ]
    t_fin = Table(fin_data, colWidths=[150, 100, 254])
    t_fin.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_fin)
    story.append(Spacer(1, 8))

    # Section 7 & 8: Recommendations & Missing Docs Checklist
    story.append(Paragraph("7. RECOMMENDED INVESTIGATION & RECOVERY ACTIONS", h1_style))
    for act in report_dossier.get("recommended_actions", []):
        story.append(Paragraph(f"• {act}", body_style))
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 6))

    story.append(Paragraph("8. MISSING DOCUMENTATION & RFI AUDIT", h1_style))
    for mdoc in report_dossier.get("missing_documentation_checklist", []):
        story.append(Paragraph(f"• [CHECKLIST] {mdoc}", body_style))
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 10))

    # Section 9: Human Reviewer Sign-off Gate (HITL)
    signoff_data = [
        [Paragraph("<b>9. HUMAN-IN-THE-LOOP ADJUSTER SIGN-OFF & GOVERNANCE DECISION</b>", body_bold), Paragraph("", body_style)],
        [Paragraph("<b>Adjuster Decision:</b> [  ] Approved  [  ] Modified  [  ] Rejected  [  ] Escalated", body_style), Paragraph("<b>Adjuster Signature:</b> ___________________________", body_style)],
        [Paragraph("<b>Authorized Name:</b> ___________________________", body_style), Paragraph("<b>Review Date:</b> ___________________________", body_style)],
        [Paragraph("<b>Adjuster Notes / Modifications:</b>", body_style), Paragraph("", body_style)],
        [Paragraph("__________________________________________________________________________________________________", body_style), Paragraph("", body_style)]
    ]
    t_sign = Table(signoff_data, colWidths=[280, 224])
    t_sign.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ("SPAN", (0, 0), (1, 0)),
        ("SPAN", (0, 3), (1, 3)),
        ("SPAN", (0, 4), (1, 4)),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(KeepTogether(t_sign))
    story.append(Spacer(1, 10))

    # Section 10: Legal Compliance Disclaimer
    disclaimer_text = report_dossier.get("governance_disclaimer", "")
    t_disc = Table([[Paragraph(f"<b>LEGAL NOTICE:</b> {disclaimer_text}", alert_style)]], colWidths=[504])
    t_disc.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(KeepTogether(t_disc))

    # Build PDF with dynamic page numbering
    doc.build(story, canvasmaker=NumberedCanvas)
    logger.info(f"Generated official Subrogation Investigation Report PDF at: {output_path}")
    return output_path

if __name__ == "__main__":
    from agents.workflow import run_investigation_workflow
    state = run_investigation_workflow("CLM-0001")
    pdf_path = generate_subrogation_pdf(state.investigation_report)
    print("ReportLab PDF generated successfully at:", pdf_path)
