"""
SQUAD-CSHARP - Tests du module RAG
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))


def test_conversational_prompt():
    """Teste la construction d'un prompt avec historique."""
    from src.rag.prompt_builder import build_conversational_prompt

    docs = [
        {
            "document": "Les interfaces en C# définissent un contrat.",
            "metadata": {"source": "doc.pdf", "page": 10, "content_type": "text"},
            "distance": 0.2,
        },
    ]

    history = [
        {"role": "user", "content": "Qu'est-ce qu'une classe ?"},
        {"role": "assistant", "content": "Une classe est un modèle..."},
    ]

    prompt = build_conversational_prompt(
        "Et une interface ?", docs, history
    )

    assert "HISTORIQUE DE CONVERSATION" in prompt
    assert "Qu'est-ce qu'une classe" in prompt
    assert "Et une interface ?" in prompt
    assert "Les interfaces en C#" in prompt

    print("✓ test_conversational_prompt")


def test_conversational_prompt_no_history():
    """Teste le prompt conversationnel sans historique."""
    from src.rag.prompt_builder import build_conversational_prompt

    docs = [
        {
            "document": "LINQ est un outil puissant.",
            "metadata": {"source": "linq.pdf", "page": 1, "content_type": "text"},
            "distance": 0.3,
        },
    ]

    prompt = build_conversational_prompt("Comment fonctionne LINQ ?", docs)

    assert "HISTORIQUE DE CONVERSATION" not in prompt
    assert "Comment fonctionne LINQ" in prompt

    print("✓ test_conversational_prompt_no_history")


def test_system_prompt_exists():
    """Vérifie que le system prompt est correctement défini."""
    from src.rag.prompt_builder import SYSTEM_PROMPT

    assert len(SYSTEM_PROMPT) > 100, "System prompt trop court"
    assert "SQUAD-CSHARP" in SYSTEM_PROMPT
    assert "C#" in SYSTEM_PROMPT

    print("✓ test_system_prompt_exists")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("SQUAD-CSHARP - Tests RAG")
    print("=" * 50 + "\n")

    tests = [
        test_conversational_prompt,
        test_conversational_prompt_no_history,
        test_system_prompt_exists,
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
