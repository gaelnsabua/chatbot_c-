"""
SQUAD-CSHARP - Tests du module d'ingestion
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))


def test_text_splitter():
    """Teste le découpage de texte en chunks."""
    from src.ingestion.text_splitter import split_document, detect_content_type

    sample_text = """
    --- Page 1 ---

    Introduction au C#

    C# est un langage de programmation moderne, orienté objet, développé par Microsoft.
    Il est utilisé pour créer des applications Windows, des services web, et des jeux vidéo.

    --- Page 2 ---

    Les types de données

    public class Program
    {
        static void Main(string[] args)
        {
            int age = 25;
            string name = "SQUAD";
            Console.WriteLine($"Hello {name}, age {age}");
        }
    }

    Les types primitifs en C# incluent int, float, double, char, bool et string.
    """

    chunks = split_document(sample_text, "test.pdf", chunk_size=200, chunk_overlap=50)

    assert len(chunks) > 0, "Le splitter devrait produire au moins un chunk"
    assert all(c.source == "test.pdf" for c in chunks), "Tous les chunks doivent avoir la bonne source"
    assert all(len(c.text) > 0 for c in chunks), "Aucun chunk ne doit être vide"

    print(f"✓ test_text_splitter : {len(chunks)} chunks créés")

    # Test détection de type de contenu
    code_text = """
    public class MyClass
    {
        public void MyMethod()
        {
            string result = "test";
            Console.WriteLine(result);
        }
    }
    """
    assert detect_content_type(code_text) == "code", "Devrait détecter du code"
    assert detect_content_type("Bonjour, ceci est un texte simple.") == "text"

    print("✓ test_detect_content_type")


def test_pdf_loader_invalid():
    """Teste le chargement d'un PDF inexistant."""
    from src.ingestion.pdf_loader import extract_text_from_pdf

    result = extract_text_from_pdf(Path("inexistant.pdf"))
    assert result is None, "Un PDF inexistant doit retourner None"

    print("✓ test_pdf_loader_invalid")


def test_prompt_builder():
    """Teste la construction des prompts."""
    from src.rag.prompt_builder import build_prompt, build_context

    docs = [
        {
            "document": "C# est un langage orienté objet.",
            "metadata": {"source": "cours.pdf", "page": 1, "content_type": "text"},
            "distance": 0.25,
        },
        {
            "document": "LINQ permet de requêter des collections.",
            "metadata": {"source": "linq.pdf", "page": 5, "content_type": "text"},
            "distance": 0.35,
        },
    ]

    context = build_context(docs)
    assert "cours.pdf" in context
    assert "linq.pdf" in context
    assert "C# est un langage" in context

    prompt = build_prompt("Qu'est-ce que C# ?", docs)
    assert "CONTEXTE DOCUMENTAIRE" in prompt
    assert "QUESTION DE L'UTILISATEUR" in prompt
    assert "Qu'est-ce que C# ?" in prompt

    print("✓ test_prompt_builder")


def test_prompt_builder_empty():
    """Teste le prompt builder sans documents."""
    from src.rag.prompt_builder import build_context

    context = build_context([])
    assert "Aucun document" in context

    print("✓ test_prompt_builder_empty")


def test_config():
    """Teste que la configuration est correctement chargée."""
    from src.utils.config import (
        OLLAMA_BASE_URL,
        OLLAMA_MODEL,
        EMBEDDING_MODEL,
        CHUNK_SIZE,
        CHUNK_OVERLAP,
        TOP_K_RETRIEVAL,
    )

    assert OLLAMA_BASE_URL.startswith("http"), "URL Ollama invalide"
    assert len(OLLAMA_MODEL) > 0, "Modèle Ollama non défini"
    assert len(EMBEDDING_MODEL) > 0, "Modèle embeddings non défini"
    assert CHUNK_SIZE > 0, "CHUNK_SIZE doit être > 0"
    assert CHUNK_OVERLAP >= 0, "CHUNK_OVERLAP doit être >= 0"
    assert CHUNK_OVERLAP < CHUNK_SIZE, "OVERLAP doit être < CHUNK_SIZE"
    assert TOP_K_RETRIEVAL > 0, "TOP_K doit être > 0"

    print("✓ test_config")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("SQUAD-CSHARP - Tests Unitaires")
    print("=" * 50 + "\n")

    tests = [
        test_config,
        test_text_splitter,
        test_pdf_loader_invalid,
        test_prompt_builder,
        test_prompt_builder_empty,
    ]

    passed = 0
    failed = 0

    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"✗ {test_fn.__name__} : {e}")
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"Résultats : {passed} passés, {failed} échoués sur {len(tests)}")
    print("=" * 50 + "\n")

    sys.exit(1 if failed > 0 else 0)
