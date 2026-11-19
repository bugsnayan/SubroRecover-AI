"""
SubroRecover AI - Vector Embeddings & ChromaDB Storage Module
Manages vector collections and persistent embeddings for insurance documents.
"""

import os
import sys
import logging
from typing import List, Dict, Any
import chromadb

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logger = logging.getLogger("subrorecover.rag.embeddings")

DEFAULT_CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = "subro_evidence_collection"

class VectorStore:
    """Interfaces with ChromaDB for embedding storage and semantic similarity queries."""

    def __init__(self, persist_dir: str = DEFAULT_CHROMA_DIR):
        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Insurance claim evidence and police crash report embeddings"}
        )
        logger.info(f"Initialized ChromaDB vector store at '{self.persist_dir}' with collection '{COLLECTION_NAME}'")

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """Indexes text chunks with their metadata into ChromaDB."""
        if not chunks:
            return 0

        documents = []
        ids = []
        metadatas = []

        for chunk in chunks:
            cid = chunk["chunk_id"]
            text = chunk["text"]
            meta = {
                "claim_id": str(chunk.get("claim_id", "UNKNOWN")),
                "document_name": str(chunk.get("document_name", "doc")),
                "document_type": str(chunk.get("document_type", "General")),
                "page_number": int(chunk.get("page_number", 1)),
                "is_verified": bool(chunk.get("is_verified", True))
            }
            documents.append(text)
            ids.append(cid)
            metadatas.append(meta)

        self.collection.upsert(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        logger.info(f"Successfully indexed {len(documents)} document chunks into vector store.")
        return len(documents)

    def query(self, query_text: str, n_results: int = 3, claim_id: str = None) -> List[Dict[str, Any]]:
        """Queries the vector store for top semantic matches."""
        where_filter = {"claim_id": claim_id} if claim_id else None

        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where_filter
        )

        formatted_matches = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
            ids = results["ids"][0] if "ids" in results else [""] * len(docs)

            for doc, meta, dist, cid in zip(docs, metas, distances, ids):
                # Calculate relevance score from distance (cosine / L2)
                sim_score = max(0.0, min(1.0, round(1.0 - (dist / 2.0), 4)))
                formatted_matches.append({
                    "chunk_id": cid,
                    "text": doc,
                    "metadata": meta,
                    "similarity_score": sim_score
                })

        return formatted_matches
