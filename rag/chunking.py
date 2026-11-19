"""
SubroRecover AI - RAG Text Chunking Module
Splits extracted document texts into semantically coherent chunks with overlap and provenance metadata.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger("subrorecover.rag.chunking")

class SemanticChunker:
    """Chunks text while preserving sentence boundaries and metadata attribution."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 80):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, doc_data: Dict[str, Any], claim_id: str = "UNKNOWN", doc_type: str = "Police Report", is_verified: bool = True) -> List[Dict[str, Any]]:
        chunks = []
        doc_name = doc_data.get("file_name", "document.pdf")

        for page in doc_data.get("pages", []):
            page_num = page["page_number"]
            text = page["text"]
            if not text:
                continue

            # Split by paragraphs or sentences
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            current_chunk = ""

            for para in paragraphs:
                if len(current_chunk) + len(para) <= self.chunk_size:
                    current_chunk += ("\n\n" if current_chunk else "") + para
                else:
                    if current_chunk:
                        chunk_id = f"{doc_name}_p{page_num}_c{len(chunks)+1}"
                        chunks.append({
                            "chunk_id": chunk_id,
                            "claim_id": claim_id,
                            "document_name": doc_name,
                            "document_type": doc_type,
                            "page_number": page_num,
                            "text": current_chunk,
                            "is_verified": is_verified
                        })
                    # Start new chunk with overlap if possible
                    overlap_prefix = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else ""
                    current_chunk = (overlap_prefix + " " + para).strip()

            if current_chunk:
                chunk_id = f"{doc_name}_p{page_num}_c{len(chunks)+1}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "claim_id": claim_id,
                    "document_name": doc_name,
                    "document_type": doc_type,
                    "page_number": page_num,
                    "text": current_chunk,
                    "is_verified": is_verified
                })

        logger.info(f"Chunked '{doc_name}' into {len(chunks)} contextual chunks.")
        return chunks
