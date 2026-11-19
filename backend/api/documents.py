"""
SubroRecover AI - Document Ingestion & RAG Indexing API Endpoints
"""

import os
import sys
import uuid
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from sqlalchemy import text

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from database.connection import engine
from rag.retriever import EvidenceRetriever

logger = logging.getLogger("subrorecover.api.documents")
router = APIRouter(prefix="/claims", tags=["Documents"])

retriever = EvidenceRetriever()
UPLOAD_DIR = "uploaded_documents"

@router.post("/{claim_id}/documents")
async def upload_claim_document(
    claim_id: str,
    file: UploadFile = File(...),
    document_type: str = Form("Police Crash Report"),
    is_verified: bool = Form(True)
):
    """
    Uploads a PDF document for a claim, extracts text, triggers ChromaDB RAG indexing,
    and updates the evidence_documents table.
    """
    # Verify claim exists
    with engine.connect() as conn:
        claim_exists = conn.execute(text("SELECT 1 FROM insurance_claims WHERE claim_id = :cid"), {"cid": claim_id}).scalar()
        if not claim_exists:
            raise HTTPException(status_code=404, detail=f"Claim '{claim_id}' not found.")

    # Validate file extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF documents are supported for RAG analysis.")

    claim_dir = os.path.join(UPLOAD_DIR, claim_id)
    os.makedirs(claim_dir, exist_ok=True)
    file_path = os.path.join(claim_dir, file.filename)

    # Save to disk
    contents = await file.read()
    file_size = len(contents)
    if file_size > 15 * 1024 * 1024:  # 15MB limit
        raise HTTPException(status_code=400, detail="Document exceeds maximum file size limit (15MB).")

    with open(file_path, "wb") as f:
        f.write(contents)

    # Index with RAG retriever
    indexed_chunks = retriever.index_pdf(
        file_path=file_path,
        claim_id=claim_id,
        doc_type=document_type,
        is_verified=is_verified
    )

    # Record in database
    doc_id = f"DOC-{uuid.uuid4().hex[:6].upper()}"
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO evidence_documents (
                document_id, claim_id, document_name, document_type,
                file_path, file_size_bytes, extracted_text,
                ocr_confidence, is_verified
            ) VALUES (
                :did, :cid, :dname, :dtype, :fpath, :fsize, :text, 0.98, :ver
            )
        """), {
            "did": doc_id,
            "cid": claim_id,
            "dname": file.filename,
            "dtype": document_type,
            "fpath": file_path,
            "fsize": file_size,
            "text": f"Indexed {indexed_chunks} chunks via ChromaDB RAG.",
            "ver": is_verified
        })

    logger.info(f"Uploaded and indexed document '{file.filename}' for claim {claim_id} ({indexed_chunks} chunks).")
    return {
        "status": "SUCCESS",
        "document_id": doc_id,
        "claim_id": claim_id,
        "file_name": file.filename,
        "file_size_bytes": file_size,
        "indexed_chunks": indexed_chunks,
        "is_verified": is_verified
    }
