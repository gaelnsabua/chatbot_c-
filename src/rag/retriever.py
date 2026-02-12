"""
SQUAD-CSHARP - Retriever
Recherche de similarité dans la base vectorielle.
"""

from src.ingestion.vector_store import VectorStore
from src.utils.config import TOP_K_RETRIEVAL
from src.utils.logger import logger


class Retriever:
    """Recherche les documents pertinents dans ChromaDB."""

    def __init__(self, vector_store: VectorStore, top_k: int = None):
        self.vector_store = vector_store
        self.top_k = top_k or TOP_K_RETRIEVAL

    def retrieve(self, question: str, top_k: int = None) -> list[dict]:
        """
        Recherche les chunks les plus pertinents pour une question.

        Args:
            question: Question de l'utilisateur.
            top_k: Nombre de résultats (override la valeur par défaut).

        Returns:
            Liste de dictionnaires avec 'document', 'metadata', 'distance'.
        """
        k = top_k or self.top_k

        logger.info(f"Recherche de {k} chunks pertinents pour : '{question[:80]}...'")

        results = self.vector_store.query(question, top_k=k)

        # Reformater les résultats
        formatted = []
        if results and results.get("documents"):
            for i in range(len(results["documents"][0])):
                formatted.append(
                    {
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "distance": results["distances"][0][i] if results.get("distances") else 0,
                    }
                )

        logger.info(f"✓ {len(formatted)} chunks trouvés")
        for i, doc in enumerate(formatted):
            src = doc["metadata"].get("source", "?")
            dist = doc["distance"]
            logger.debug(f"  [{i+1}] source={src}, distance={dist:.4f}")

        return formatted

    def retrieve_with_threshold(
        self, question: str, top_k: int = None, max_distance: float = 1.5
    ) -> list[dict]:
        """
        Recherche avec filtrage par seuil de distance.

        Args:
            question: Question de l'utilisateur.
            top_k: Nombre de résultats maximum.
            max_distance: Distance maximale (les résultats au-delà sont écartés).

        Returns:
            Liste filtrée de résultats.
        """
        results = self.retrieve(question, top_k)
        filtered = [r for r in results if r["distance"] <= max_distance]

        if len(filtered) < len(results):
            logger.info(
                f"Filtrage : {len(results)} → {len(filtered)} résultats "
                f"(seuil distance = {max_distance})"
            )

        return filtered
