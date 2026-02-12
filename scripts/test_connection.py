"""
SQUAD-CSHARP - Test de connexion
Vérifie que tous les composants sont opérationnels.

Usage:
    python scripts/test_connection.py
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from rich.console import Console
from rich.panel import Panel

from src.utils.validators import validate_system_ready, check_ollama_running, check_model_exists
from src.utils.config import get_config_summary, OLLAMA_MODEL

console = Console()


def main():
    console.print("\n[bold cyan]🔍 SQUAD-CSHARP - Test de connexion[/bold cyan]\n")

    # Configuration
    config = get_config_summary()
    console.print(Panel(
        "\n".join(f"[bold]{k}[/bold] : {v}" for k, v in config.items()),
        title="⚙️ Configuration",
        border_style="blue",
    ))

    console.print()

    # Tests
    tests = []

    # Test 1 : Ollama accessible
    console.print("1. Test connexion Ollama...", end=" ")
    ollama_ok = check_ollama_running()
    if ollama_ok:
        console.print("[bold green]✓ OK[/bold green]")
    else:
        console.print("[bold red]✗ ÉCHEC[/bold red]")
        console.print("   → Lancez Ollama avec : [bold]ollama serve[/bold]")
    tests.append(("Ollama", ollama_ok))

    # Test 2 : Modèle disponible
    console.print(f"2. Test modèle '{OLLAMA_MODEL}'...", end=" ")
    model_ok = check_model_exists() if ollama_ok else False
    if model_ok:
        console.print("[bold green]✓ OK[/bold green]")
    else:
        console.print("[bold red]✗ ÉCHEC[/bold red]")
        console.print(f"   → Créez le modèle : [bold]cd models && ollama create {OLLAMA_MODEL} -f Modelfile[/bold]")
    tests.append(("Modèle", model_ok))

    # Test 3 : ChromaDB
    console.print("3. Test ChromaDB...", end=" ")
    try:
        from src.ingestion.vector_store import VectorStore
        vs = VectorStore()
        stats = vs.get_stats()
        console.print(f"[bold green]✓ OK[/bold green] ({stats['total_documents']} documents)")
        tests.append(("ChromaDB", True))
    except Exception as e:
        console.print(f"[bold red]✗ ÉCHEC ({e})[/bold red]")
        tests.append(("ChromaDB", False))

    # Test 4 : Génération LLM (si tout est OK)
    if ollama_ok and model_ok:
        console.print("4. Test génération LLM...", end=" ")
        try:
            from src.rag.llm_handler import LLMHandler
            llm = LLMHandler()
            ok = llm.test_connection()
            if ok:
                console.print("[bold green]✓ OK[/bold green]")
            else:
                console.print("[bold red]✗ ÉCHEC[/bold red]")
            tests.append(("LLM", ok))
        except Exception as e:
            console.print(f"[bold red]✗ ÉCHEC ({e})[/bold red]")
            tests.append(("LLM", False))
    else:
        console.print("4. Test LLM... [yellow]⏭ PASSÉ (Ollama non disponible)[/yellow]")
        tests.append(("LLM", False))

    # Résumé
    console.print()
    all_ok = all(t[1] for t in tests)
    if all_ok:
        console.print(Panel(
            "[bold green]✅ Tous les tests sont passés ! Le système est prêt.[/bold green]",
            border_style="green",
        ))
    else:
        failed = [t[0] for t in tests if not t[1]]
        console.print(Panel(
            f"[bold red]❌ Tests échoués : {', '.join(failed)}[/bold red]\n"
            "Consultez le README.md pour les instructions d'installation.",
            border_style="red",
        ))


if __name__ == "__main__":
    main()
