"""
SQUAD-CSHARP - Interface CLI
Interface en ligne de commande pour le chatbot expert C#.
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from src.ingestion.vector_store import VectorStore
from src.rag.retriever import Retriever
from src.rag.prompt_builder import build_conversational_prompt, is_technical_question, is_off_topic
from src.rag.llm_handler import LLMHandler
from src.utils.config import TOP_K_RETRIEVAL, OLLAMA_MODEL

console = Console()


def print_banner():
    """Affiche la bannière d'accueil."""
    banner = """
[bold cyan]╔══════════════════════════════════════════╗
║         🎯 SQUAD-CSHARP v1.0            ║
║   Assistant Expert C# — 100% Local      ║
╚══════════════════════════════════════════╝[/bold cyan]
    """
    console.print(banner)
    console.print(
        "[dim]Tapez votre question sur le C#. "
        "Commandes : /quit, /stats, /clear, /help[/dim]\n"
    )


def print_sources(docs: list[dict]):
    """Affiche les sources documentaires."""
    if not docs:
        return

    table = Table(title="📚 Sources", show_header=True, header_style="bold magenta")
    table.add_column("#", width=3)
    table.add_column("Source", style="cyan")
    table.add_column("Page", justify="center", width=6)
    table.add_column("Distance", justify="center", width=10)

    for i, doc in enumerate(docs):
        table.add_row(
            str(i + 1),
            doc["metadata"].get("source", "?"),
            str(doc["metadata"].get("page", "?")),
            f"{doc['distance']:.4f}",
        )

    console.print(table)
    console.print()


def handle_command(command: str, vector_store: VectorStore) -> bool:
    """
    Gère les commandes spéciales.

    Returns:
        True pour continuer, False pour quitter.
    """
    cmd = command.strip().lower()

    if cmd in ("/quit", "/exit", "/q"):
        console.print("\n[bold cyan]Au revoir ! 👋[/bold cyan]\n")
        return False

    elif cmd == "/stats":
        stats = vector_store.get_stats()
        console.print(Panel(
            f"[bold]Collection[/bold] : {stats['collection_name']}\n"
            f"[bold]Documents[/bold] : {stats['total_documents']}\n"
            f"[bold]Modèle Embeddings[/bold] : {stats['embedding_model']}\n"
            f"[bold]Modèle LLM[/bold] : {OLLAMA_MODEL}",
            title="📊 Statistiques",
            border_style="green",
        ))

    elif cmd == "/clear":
        console.clear()
        print_banner()

    elif cmd == "/help":
        console.print(Panel(
            "[bold]/quit[/bold]  — Quitter l'application\n"
            "[bold]/stats[/bold] — Afficher les statistiques\n"
            "[bold]/clear[/bold] — Effacer l'écran\n"
            "[bold]/help[/bold]  — Afficher cette aide",
            title="❓ Commandes disponibles",
            border_style="blue",
        ))

    else:
        console.print(f"[red]Commande inconnue : {command}[/red]")

    return True


def main():
    """Point d'entrée de l'interface CLI."""
    print_banner()

    # Initialisation
    with console.status("[bold green]Chargement de la base de connaissances..."):
        try:
            vector_store = VectorStore()
            retriever = Retriever(vector_store, top_k=TOP_K_RETRIEVAL)
            llm = LLMHandler()
        except Exception as e:
            console.print(f"[bold red]Erreur d'initialisation : {e}[/bold red]")
            console.print(
                "\nVérifiez que :\n"
                "1. Ollama est démarré (ollama serve)\n"
                f"2. Le modèle '{OLLAMA_MODEL}' existe (ollama list)\n"
                "3. La base a été alimentée (python scripts/ingest_pdfs.py)\n"
            )
            return

    stats = vector_store.get_stats()
    console.print(
        f"[green]✓ Prêt ! {stats['total_documents']} documents en base.[/green]\n"
    )

    history = []

    # Boucle principale
    while True:
        try:
            question = Prompt.ask("\n[bold cyan]Vous[/bold cyan]")

            if not question.strip():
                continue

            if question.startswith("/"):
                if not handle_command(question, vector_store):
                    break
                continue

            # Recherche de contexte (seulement pour les questions techniques C#)
            docs = []
            if is_technical_question(question) and not is_off_topic(question):
                with console.status("[bold yellow]Recherche dans la documentation..."):
                    docs = retriever.retrieve(question)

            # Génération
            full_prompt = build_conversational_prompt(question, docs, history)

            console.print("\n[bold green]SQUAD-CSHARP[/bold green] :")
            response = llm.generate(full_prompt)
            console.print(Markdown(response))

            # Sources
            print_sources(docs)

            # Historique
            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": response})

            # Limiter l'historique
            if len(history) > 20:
                history = history[-20:]

        except KeyboardInterrupt:
            console.print("\n\n[bold cyan]Au revoir ! 👋[/bold cyan]\n")
            break
        except Exception as e:
            console.print(f"[bold red]Erreur : {e}[/bold red]")


if __name__ == "__main__":
    main()
