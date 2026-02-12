"""
SQUAD-CSHARP - Module Utilitaires
Configuration centralisée du projet.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# === Chemins ===
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PDF_DIR = DATA_DIR / "pdfs"
CHROMA_DIR = Path(os.getenv("CHROMA_PERSIST_DIRECTORY", str(DATA_DIR / "chroma_db")))
METADATA_DIR = DATA_DIR / "metadata"
LOG_DIR = PROJECT_ROOT / "logs"

# === Ollama ===
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "SQUAD-CSHARP")

# === Embeddings ===
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# === ChromaDB ===
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "csharp_knowledge")

# === RAG ===
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "5"))

# === Logging ===
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(LOG_DIR / "squad_csharp.log"))

# === LLM Parameters ===
LLM_TEMPERATURE = 0.3
LLM_TOP_P = 0.9
LLM_NUM_CTX = 4096


def ensure_directories():
    """Crée les répertoires nécessaires s'ils n'existent pas."""
    for directory in [DATA_DIR, PDF_DIR, CHROMA_DIR, METADATA_DIR, LOG_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def get_config_summary() -> dict:
    """Retourne un résumé de la configuration actuelle."""
    return {
        "project_root": str(PROJECT_ROOT),
        "ollama_url": OLLAMA_BASE_URL,
        "ollama_model": OLLAMA_MODEL,
        "embedding_model": EMBEDDING_MODEL,
        "chroma_dir": str(CHROMA_DIR),
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "top_k": TOP_K_RETRIEVAL,
    }
