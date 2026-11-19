"""
SubroRecover AI - RAG Document Loader
Extracts, cleans, and structures text from PDF documents (police reports, estimates, statements).
"""

import os
import re
import logging
from typing import Dict, Any, List
import pypdf

logger = logging.getLogger("subrorecover.rag.loader")

class DocumentLoader:
    """Loads and normalizes text from PDF claim files."""

    @staticmethod
    def load_pdf(file_path: str) -> Dict[str, Any]:
        """Reads a PDF file using pypdf and extracts clean text per page."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF document not found: {file_path}")

        reader = pypdf.PdfReader(file_path)
        pages_content = []
        full_text = []

        for idx, page in enumerate(reader.pages):
            raw_text = page.extract_text() or ""
            cleaned = DocumentLoader.clean_text(raw_text)
            pages_content.append({
                "page_number": idx + 1,
                "text": cleaned,
                "char_count": len(cleaned)
            })
            full_text.append(cleaned)

        doc_meta = {
            "file_name": os.path.basename(file_path),
            "file_path": file_path,
            "total_pages": len(reader.pages),
            "total_chars": sum(p["char_count"] for p in pages_content),
            "pages": pages_content,
            "full_text": "\n\n".join(full_text)
        }
        logger.info(f"Loaded PDF '{doc_meta['file_name']}' ({doc_meta['total_pages']} pages, {doc_meta['total_chars']} chars)")
        return doc_meta

    @staticmethod
    def clean_text(text: str) -> str:
        """Removes excessive whitespace and irregular control characters."""
        if not text:
            return ""
        # Normalize multiple spaces and line breaks
        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
