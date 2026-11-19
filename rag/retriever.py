"""
SubroRecover AI - Contextual Semantic Retriever Module
Retrieves grounded evidence passages and categorizes findings into verified facts, unverified statements, and missing information.
"""

import os
import sys
import logging
from typing import Dict, Any, List

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag.document_loader import DocumentLoader
from rag.chunking import SemanticChunker
from rag.embeddings import VectorStore

logger = logging.getLogger("subrorecover.rag.retriever")

class EvidenceRetriever:
    """Manages document ingestion, indexing, and context-grounded retrieval."""

    def __init__(self, vector_store: VectorStore = None):
        self.vector_store = vector_store or VectorStore()
        self.loader = DocumentLoader()
        self.chunker = SemanticChunker()

    def index_pdf(self, file_path: str, claim_id: str, doc_type: str = "Police Crash Report", is_verified: bool = True) -> int:
        """Loads a PDF, breaks into semantic chunks, and indexes in ChromaDB."""
        if not os.path.exists(file_path):
            logger.warning(f"File path does not exist for indexing: {file_path}")
            return 0

        doc_data = self.loader.load_pdf(file_path)
        chunks = self.chunker.chunk_document(doc_data, claim_id=claim_id, doc_type=doc_type, is_verified=is_verified)
        count = self.vector_store.add_chunks(chunks)
        logger.info(f"Indexed {count} chunks for claim {claim_id} from {file_path}")
        return count

    def retrieve_context(self, claim_id: str, query: str = "accident cause point of impact citations", top_k: int = 3) -> Dict[str, Any]:
        """
        Retrieves relevant passages and segments evidence into verified facts,
        unverified claims, citations, and identified evidentiary gaps.
        """
        matches = self.vector_store.query(query_text=query, n_results=top_k, claim_id=claim_id)

        verified_facts = []
        unverified_statements = []
        citations_found = []
        source_references = []

        for m in matches:
            text = m["text"]
            meta = m["metadata"]
            doc_name = meta.get("document_name", "Evidence Document")
            page = meta.get("page_number", 1)
            is_ver = meta.get("is_verified", False)

            ref_entry = {
                "source": f"{doc_name} (Page {page})",
                "excerpt": text[:200] + ("..." if len(text) > 200 else ""),
                "similarity": m["similarity_score"],
                "verified": is_ver
            }
            source_references.append(ref_entry)

            # Categorize facts vs unverified
            if is_ver and ("police" in doc_name.lower() or "officer" in text.lower()):
                verified_facts.append(f"[{doc_name} p.{page}]: {text}")
                # Check for statutory citations in excerpt
                if "sec." in text.lower() or "violation" in text.lower() or "citation" in text.lower():
                    citations_found.append(text)
            else:
                unverified_statements.append(f"[{doc_name} p.{page}]: {text}")

        # Check for missing evidentiary gaps
        missing_evidence = []
        if not verified_facts:
            missing_evidence.append("Official certified police collision report is missing or unverified.")
        if not citations_found:
            missing_evidence.append("No explicit statutory citation records found in current file.")

        return {
            "claim_id": claim_id,
            "query": query,
            "matches_count": len(matches),
            "verified_facts": verified_facts,
            "unverified_statements": unverified_statements,
            "citations_found": citations_found,
            "missing_evidence": missing_evidence,
            "source_references": source_references
        }

if __name__ == "__main__":
    retriever = EvidenceRetriever()
    # Index sample police reports
    p1 = "sample_data/pdfs/CLM-0001_police_report.pdf"
    p2 = "sample_data/pdfs/CLM-0002_police_report.pdf"
    if os.path.exists(p1):
        retriever.index_pdf(p1, claim_id="CLM-0001", doc_type="Police Crash Report", is_verified=True)
    if os.path.exists(p2):
        retriever.index_pdf(p2, claim_id="CLM-0002", doc_type="Police Crash Report", is_verified=True)

    res = retriever.retrieve_context("CLM-0001", "rear-end speed traffic signal violation")
    print("Retrieved Context for CLM-0001:")
    print("Verified Facts:", len(res["verified_facts"]))
    print("Source References:", res["source_references"])
