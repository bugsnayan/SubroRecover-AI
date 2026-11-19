"""
SubroRecover AI - Agent 2: Evidence Analysis Agent
Audits police crash reports, witness accounts, and documents via RAG retrieval to extract verified facts and citations.
"""

import os
import sys
import time
import logging
from typing import Dict, Any, List

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.state import SubroRecoverState
from rag.retriever import EvidenceRetriever
from agents.llm_client import call_llm

logger = logging.getLogger("subrorecover.agents.evidence_agent")

class EvidenceAnalysisAgent:
    """Agent 2: Conducts evidentiary audits using semantic retrieval and provenance verification."""

    def __init__(self, retriever: EvidenceRetriever = None):
        self.name = "Evidence Analysis Agent"
        self.retriever = retriever or EvidenceRetriever()

    def execute(self, state: SubroRecoverState) -> SubroRecoverState:
        start_time = time.time()
        logger.info(f"[{self.name}] Auditing evidence for claim {state.claim_id}...")

        report = state.accident_report_data or {}
        parties = state.involved_parties or []

        # 1. RAG Semantic Retrieval on Claim Dossier
        query_text = f"{report.get('primary_contributing_factor', '')} {report.get('citations_issued', '')} impact collision fault"
        rag_context = self.retriever.retrieve_context(claim_id=state.claim_id, query=query_text, top_k=3)

        verified_facts = list(rag_context.get("verified_facts", []))
        unverified_facts = list(rag_context.get("unverified_statements", []))
        citations = list(rag_context.get("citations_found", []))
        source_refs = list(rag_context.get("source_references", []))

        # 2. Extract Official Police Narrative if present in DB
        police_narrative = report.get("officer_narrative", "")
        police_no = report.get("police_report_number", "N/A")
        citations_db = report.get("citations_issued", "None")

        if police_narrative and police_no != "N/A":
            fact_entry = f"[Accident Report #{police_no}]: {police_narrative}"
            if fact_entry not in verified_facts:
                verified_facts.append(fact_entry)
            if citations_db and citations_db != "None" and citations_db not in citations:
                citations.append(f"Statutory Citation: {citations_db}")

        # 3. Extract Involved Parties Dossier
        adverse_driver = None
        insured_driver = None
        for p in parties:
            ptype = p.get("party_type", "")
            if "Adverse" in ptype:
                adverse_driver = p
            elif "Insured" in ptype:
                insured_driver = p

        # 4. Check for Conflicting Statements
        conflicting_notes = []
        if adverse_driver and insured_driver:
            adv_stmt = adverse_driver.get("statement_summary", "")
            ins_stmt = insured_driver.get("statement_summary", "")
            if "disputed" in adv_stmt.lower() or "denied" in adv_stmt.lower():
                conflicting_notes.append("Adverse driver disputes liability assertion made by insured operator.")

        # 5. LLM Synthesis or Deterministic Grounded Reasoning
        llm_prompt = f"""You are an Evidence Audit Specialist. Review these verified facts and statutory citations:
Facts: {verified_facts}
Citations: {citations}
Parties: Adverse Carrier: {adverse_driver.get('insurance_carrier', 'Unknown') if adverse_driver else 'None'}
Provide a 2-sentence evidentiary assessment summarizing evidence strength."""

        llm_response = call_llm(llm_prompt, system_instruction="Provide objective, legally grounded evidentiary findings.")
        mode = "LIVE_LLM (Gemini)" if llm_response else "LOCAL_DETERMINISTIC_RULES"

        if llm_response:
            evidence_summary = llm_response.strip()
        else:
            has_cite = bool(citations)
            evidence_summary = (
                f"Evidentiary review confirms {len(verified_facts)} verified crash fact(s). "
                f"{'Official statutory traffic citations are documented against adverse operator.' if has_cite else 'No formal traffic citations issued on scene.'} "
                f"Adverse carrier identified as {adverse_driver.get('insurance_carrier', 'Unidentified') if adverse_driver else 'Unidentified'}."
            )

        evidence_analysis = {
            "evidence_summary": evidence_summary,
            "has_police_report": police_no != "N/A",
            "police_report_number": police_no,
            "citations_documented": citations,
            "adverse_party_name": adverse_driver.get("full_name", "Unknown") if adverse_driver else "N/A",
            "adverse_carrier": adverse_driver.get("insurance_carrier", "Unknown") if adverse_driver else "N/A",
            "adverse_vehicle": adverse_driver.get("vehicle_year_make_model", "Unknown") if adverse_driver else "N/A",
            "conflicting_information": conflicting_notes,
            "mode": mode
        }

        # Update State
        state.evidence_analysis = evidence_analysis
        state.verified_facts = verified_facts
        state.unverified_facts = unverified_facts
        state.evidence_citations = citations
        state.evidence_sources = source_refs

        duration_ms = int((time.time() - start_time) * 1000)
        state.agent_logs.append({
            "agent_name": self.name,
            "step": 2,
            "status": "COMPLETED",
            "duration_ms": duration_ms,
            "mode": mode,
            "summary": f"Audited {len(verified_facts)} verified facts, {len(citations)} citations, and {len(source_refs)} sources."
        })

        logger.info(f"[{self.name}] Completed in {duration_ms}ms (Mode: {mode})")
        return state
