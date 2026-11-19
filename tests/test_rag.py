"""
SubroRecover AI - RAG & Document Intelligence Test Suite
Tests PDF text extraction, semantic chunking, and ChromaDB vector retrieval.
"""

import os
import sys
import pytest

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag.document_loader import DocumentLoader
from rag.chunking import SemanticChunker
from rag.retriever import EvidenceRetriever

def test_pdf_loading():
    sample_pdf = "sample_data/pdfs/CLM-0001_police_report.pdf"
    if os.path.exists(sample_pdf):
        doc = DocumentLoader.load_pdf(sample_pdf)
        assert doc["total_pages"] >= 1
        assert "CRASH INVESTIGATION REPORT" in doc["full_text"]

def test_chunking():
    doc_data = {
        "file_name": "test_report.pdf",
        "pages": [{"page_number": 1, "text": "Paragraph 1 describing rear-end crash.\n\nParagraph 2 describing driver statements."}]
    }
    chunker = SemanticChunker(chunk_size=100, chunk_overlap=20)
    chunks = chunker.chunk_document(doc_data, claim_id="CLM-TEST")
    assert len(chunks) >= 1
    assert chunks[0]["claim_id"] == "CLM-TEST"

def test_retriever():
    retriever = EvidenceRetriever()
    sample_pdf = "sample_data/pdfs/CLM-0001_police_report.pdf"
    if os.path.exists(sample_pdf):
        retriever.index_pdf(sample_pdf, claim_id="CLM-0001", doc_type="Police Report")
        ctx = retriever.retrieve_context("CLM-0001", "rear-end citation")
        assert ctx["claim_id"] == "CLM-0001"
        assert len(ctx["source_references"]) >= 1
