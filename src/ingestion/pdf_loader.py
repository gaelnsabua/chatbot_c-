"""
SQUAD-CSHARP - PDF Loader
Extraction de texte depuis les fichiers PDF.
"""

from pathlib import Path
from typing import Optional

from pypdf import PdfReader
from tqdm import tqdm

from src.utils.logger import logger


class PDFDocument:
    """Représente un document PDF extrait."""

    def __init__(self, source: str, text: str, pages: int, metadata: dict = None):
        self.source = source
        self.text = text
        self.pages = pages
        self.metadata = metadata or {}


def extract_text_from_pdf(pdf_path: Path) -> Optional[PDFDocument]:
    """
    Extrait le texte d'un fichier PDF.

    Args:
        pdf_path: Chemin vers le fichier PDF.

    Returns:
        PDFDocument contenant le texte extrait, ou None en cas d'erreur.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        logger.error(f"Fichier introuvable : {pdf_path}")
        return None

    if not pdf_path.suffix.lower() == ".pdf":
        logger.error(f"Le fichier n'est pas un PDF : {pdf_path}")
        return None

    try:
        reader = PdfReader(str(pdf_path))
        total_pages = len(reader.pages)
        logger.info(f"Lecture de '{pdf_path.name}' ({total_pages} pages)...")

        full_text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                # Nettoyage basique du texte
                page_text = _clean_page_text(page_text)
                full_text += f"\n\n--- Page {i + 1} ---\n\n{page_text}"

        if not full_text.strip():
            logger.warning(f"Aucun texte extrait de : {pdf_path.name}")
            return None

        doc = PDFDocument(
            source=pdf_path.name,
            text=full_text.strip(),
            pages=total_pages,
            metadata={
                "file_path": str(pdf_path),
                "file_size_mb": round(pdf_path.stat().st_size / (1024 * 1024), 2),
            },
        )

        logger.info(
            f"✓ '{pdf_path.name}' : {total_pages} pages, "
            f"{len(full_text)} caractères extraits"
        )
        return doc

    except Exception as e:
        logger.error(f"Erreur lors de la lecture de '{pdf_path.name}' : {e}")
        return None


def load_all_pdfs(pdf_dir: Path) -> list[PDFDocument]:
    """
    Charge tous les PDF d'un répertoire.

    Args:
        pdf_dir: Répertoire contenant les fichiers PDF.

    Returns:
        Liste de PDFDocument.
    """
    pdf_dir = Path(pdf_dir)
    pdf_files = sorted(pdf_dir.glob("*.pdf"))

    if not pdf_files:
        logger.warning(f"Aucun PDF trouvé dans : {pdf_dir}")
        return []

    logger.info(f"Chargement de {len(pdf_files)} fichier(s) PDF...")

    documents = []
    for pdf_path in tqdm(pdf_files, desc="Extraction PDF"):
        doc = extract_text_from_pdf(pdf_path)
        if doc:
            documents.append(doc)

    logger.info(f"✓ {len(documents)}/{len(pdf_files)} PDF extraits avec succès")
    return documents


def _clean_page_text(text: str) -> str:
    """Nettoyage basique du texte d'une page."""
    import re

    # Supprimer les espaces multiples (mais conserver les retours à la ligne)
    text = re.sub(r"[ \t]+", " ", text)

    # Supprimer les lignes vides multiples
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
