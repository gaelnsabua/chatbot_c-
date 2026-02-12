"""
SQUAD-CSHARP - Vector Store
Gestion de la base vectorielle ChromaDB avec embeddings.
"""

import json
from datetime import datetime
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from src.ingestion.text_splitter import TextChunk
from src.utils.config import (
    CHROMA_DIR,
    CHROMA_COLLECTION_NAME,
    EMBEDDING_MODEL,
    METADATA_DIR,
)
from src.utils.logger import logger


class VectorStore:
    """Gestionnaire de la base vectorielle ChromaDB."""

    def __init__(
        self,
        persist_dir: str = None,
        collection_name: str = None,
        embedding_model_name: str = None,
    ):
        self.persist_dir = Path(persist_dir or CHROMA_DIR)
        self.collection_name = collection_name or CHROMA_COLLECTION_NAME
        self.embedding_model_name = embedding_model_name or EMBEDDING_MODEL

        # Initialiser le modèle d'embeddings
        logger.info(f"Chargement du modèle d'embeddings : {self.embedding_model_name}...")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        logger.info("✓ Modèle d'embeddings chargé")

        # Initialiser ChromaDB
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.collection = self._get_or_create_collection()

        logger.info(
            f"✓ ChromaDB initialisé (collection: '{self.collection_name}', "
            f"documents: {self.collection.count()})"
        )

    def _get_or_create_collection(self):
        """Récupère ou crée la collection ChromaDB."""
        return self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Base de connaissances C# - SQUAD-CSHARP"},
        )

    def add_chunks(self, chunks: list[TextChunk], batch_size: int = 100):
        """
        Ajoute des chunks à la base vectorielle.

        Args:
            chunks: Liste de TextChunk à indexer.
            batch_size: Nombre de chunks par batch.
        """
        if not chunks:
            logger.warning("Aucun chunk à indexer")
            return

        logger.info(f"Indexation de {len(chunks)} chunks...")

        # Traiter par batch
        for i in tqdm(range(0, len(chunks), batch_size), desc="Indexation"):
            batch = chunks[i : i + batch_size]

            texts = [c.text for c in batch]
            ids = [c.chunk_id for c in batch]
            metadatas = [
                {
                    "source": c.source,
                    "page": c.page,
                    "content_type": c.content_type,
                    "char_count": c.metadata.get("char_count", 0),
                    "date_ingestion": datetime.now().isoformat(),
                }
                for c in batch
            ]

            # Générer les embeddings
            embeddings = self.embedding_model.encode(texts).tolist()

            # Ajouter à ChromaDB
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids,
            )

        total = self.collection.count()
        logger.info(f"✓ {len(chunks)} chunks indexés. Total en base : {total}")

        # Sauvegarder les métadonnées d'ingestion
        self._save_ingestion_log(chunks)

    def query(self, question: str, top_k: int = 5) -> dict:
        """
        Recherche les chunks les plus pertinents pour une question.

        Args:
            question: Question de l'utilisateur.
            top_k: Nombre de résultats à retourner.

        Returns:
            Dictionnaire avec documents, metadatas et distances.
        """
        # Vectoriser la question
        question_embedding = self.embedding_model.encode([question]).tolist()

        # Recherche dans ChromaDB
        results = self.collection.query(
            query_embeddings=question_embedding,
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        return results

    def reset(self):
        """Réinitialise la collection (supprime toutes les données)."""
        logger.warning("Réinitialisation de la base vectorielle...")
        self.client.delete_collection(self.collection_name)
        self.collection = self._get_or_create_collection()
        logger.info("✓ Base vectorielle réinitialisée")

    def get_stats(self) -> dict:
        """Retourne des statistiques sur la base vectorielle."""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "total_documents": count,
            "persist_directory": str(self.persist_dir),
            "embedding_model": self.embedding_model_name,
        }

    def _save_ingestion_log(self, chunks: list[TextChunk]):
        """Sauvegarde un log de l'ingestion."""
        METADATA_DIR.mkdir(parents=True, exist_ok=True)
        log_file = METADATA_DIR / "ingestion_log.json"

        log_data = {
            "date": datetime.now().isoformat(),
            "chunks_added": len(chunks),
            "sources": list(set(c.source for c in chunks)),
            "total_in_db": self.collection.count(),
        }

        # Charger l'historique existant
        history = []
        if log_file.exists():
            try:
                history = json.loads(log_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        history.append(log_data)
        log_file.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")
