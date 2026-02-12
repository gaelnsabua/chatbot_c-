"""
SQUAD-CSHARP - Validators
Fonctions de validation pour le projet.
"""

import requests
from pathlib import Path

from src.utils.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from src.utils.logger import logger


def check_ollama_running() -> bool:
    """Vérifie qu'Ollama est accessible."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except requests.ConnectionError:
        logger.error(f"Ollama n'est pas accessible sur {OLLAMA_BASE_URL}")
        return False


def check_model_exists() -> bool:
    """Vérifie que le modèle SQUAD-CSHARP est disponible."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]
            exists = any(OLLAMA_MODEL.lower() in name.lower() for name in model_names)
            if not exists:
                logger.warning(
                    f"Modèle '{OLLAMA_MODEL}' non trouvé. "
                    f"Modèles disponibles : {model_names}"
                )
            return exists
    except Exception as e:
        logger.error(f"Erreur vérification modèle : {e}")
    return False


def validate_pdf_directory(pdf_dir: Path) -> list[Path]:
    """Valide et retourne la liste des PDF dans un répertoire."""
    pdf_dir = Path(pdf_dir)
    if not pdf_dir.exists():
        logger.error(f"Répertoire PDF introuvable : {pdf_dir}")
        return []

    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"Aucun fichier PDF trouvé dans : {pdf_dir}")
    else:
        logger.info(f"{len(pdf_files)} fichier(s) PDF trouvé(s) dans : {pdf_dir}")

    return pdf_files


def validate_system_ready() -> dict:
    """Vérifie que tout le système est prêt."""
    status = {
        "ollama_running": check_ollama_running(),
        "model_exists": False,
        "ready": False,
    }
    if status["ollama_running"]:
        status["model_exists"] = check_model_exists()
    status["ready"] = status["ollama_running"] and status["model_exists"]
    return status
