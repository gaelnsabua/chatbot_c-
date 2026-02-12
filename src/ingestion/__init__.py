"""
SQUAD-CSHARP - Module d'Ingestion
Chargement, découpage et indexation des documents PDF.
"""

from src.ingestion.pdf_loader import extract_text_from_pdf, load_all_pdfs, PDFDocument
from src.ingestion.text_splitter import split_document, TextChunk
from src.ingestion.vector_store import VectorStore

__all__ = [
    "extract_text_from_pdf",
    "load_all_pdfs",
    "PDFDocument",
    "split_document",
    "TextChunk",
    "VectorStore",
]
