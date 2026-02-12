"""
SQUAD-CSHARP - Point d'entrée principal
Lance l'application selon le mode choisi.

Usage:
    python src/main.py                  # Lance Streamlit (par défaut)
    python src/main.py --mode cli       # Lance le mode CLI
    python src/main.py --mode streamlit # Lance Streamlit
    python src/main.py --ingest         # Lance l'ingestion des PDF
    python src/main.py --test           # Test la connexion
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Assurer le path correct
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.utils.config import ensure_directories
from src.utils.logger import logger


def run_streamlit():
    """Lance l'interface Streamlit."""
    logger.info("Démarrage de l'interface Streamlit...")
    app_path = ROOT_DIR / "src" / "ui" / "streamlit_app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])


def run_cli():
    """Lance l'interface CLI."""
    from src.ui.cli_app import main as cli_main

    cli_main()


def run_ingest():
    """Lance l'ingestion des PDF."""
    from scripts.ingest_pdfs import main as ingest_main

    ingest_main()


def run_test():
    """Lance les tests de connexion."""
    from scripts.test_connection import main as test_main

    test_main()


def main():
    parser = argparse.ArgumentParser(
        description="SQUAD-CSHARP - Assistant Expert C# 100% Local"
    )
    parser.add_argument(
        "--mode",
        choices=["streamlit", "cli"],
        default="streamlit",
        help="Mode d'interface (défaut: streamlit)",
    )
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Lancer l'ingestion des PDF",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Tester la connexion aux services",
    )
    args = parser.parse_args()

    ensure_directories()

    if args.test:
        run_test()
    elif args.ingest:
        run_ingest()
    elif args.mode == "cli":
        run_cli()
    else:
        run_streamlit()


if __name__ == "__main__":
    main()
