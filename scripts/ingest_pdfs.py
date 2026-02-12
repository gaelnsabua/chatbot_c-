"""
SQUAD-CSHARP - Script d'ingestion des PDF
Charge tous les PDF et les indexe dans ChromaDB.

Usage:
    python scripts/ingest_pdfs.py
    python scripts/ingest_pdfs.py --pdf-dir ./data/pdfs
    python scripts/ingest_pdfs.py --reset
"""

import argparse
import sys
from pathlib import Path

# Ajouter le répertoire racine au path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.ingestion.pdf_loader import load_all_pdfs
from src.ingestion.text_splitter import split_document
from src.ingestion.vector_store import VectorStore
from src.utils.config import PDF_DIR, ensure_directories
from src.utils.logger import logger


def main():
    parser = argparse.ArgumentParser(description="Ingestion des PDF dans ChromaDB")
    parser.add_argument(
        "--pdf-dir",
        type=str,
        default=str(PDF_DIR),
        help="Répertoire contenant les PDF",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Réinitialiser la base ChromaDB avant ingestion",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Taille des chunks (défaut: 1000)",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Chevauchement des chunks (défaut: 200)",
    )
    args = parser.parse_args()

    ensure_directories()

    logger.info("=" * 60)
    logger.info("SQUAD-CSHARP - Ingestion des PDF")
    logger.info("=" * 60)
    logger.info(f"Répertoire PDF : {args.pdf_dir}")

    # 1. Charger les PDF
    pdf_dir = Path(args.pdf_dir)
    documents = load_all_pdfs(pdf_dir)

    if not documents:
        logger.error("Aucun document PDF à traiter. Arrêt.")
        logger.info(f"Placez vos fichiers PDF dans : {pdf_dir}")
        return

    # 2. Découper en chunks
    all_chunks = []
    for doc in documents:
        chunks = split_document(
            doc.text, doc.source, args.chunk_size, args.chunk_overlap
        )
        all_chunks.extend(chunks)

    logger.info(f"Total : {len(all_chunks)} chunks créés à partir de {len(documents)} PDF")

    # 3. Indexer dans ChromaDB
    vector_store = VectorStore()

    if args.reset:
        vector_store.reset()

    vector_store.add_chunks(all_chunks)

    # 4. Résumé
    stats = vector_store.get_stats()
    logger.info("=" * 60)
    logger.info("INGESTION TERMINÉE")
    logger.info(f"  Documents PDF traités : {len(documents)}")
    logger.info(f"  Chunks créés          : {len(all_chunks)}")
    logger.info(f"  Total en base         : {stats['total_documents']}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
