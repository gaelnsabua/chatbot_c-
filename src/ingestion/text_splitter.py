"""
SQUAD-CSHARP - Text Splitter
Découpage intelligent du texte en chunks pour la vectorisation.
"""

import re
from dataclasses import dataclass, field

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.utils.config import CHUNK_SIZE, CHUNK_OVERLAP
from src.utils.logger import logger


@dataclass
class TextChunk:
    """Représente un segment de texte avec ses métadonnées."""

    text: str
    chunk_id: str
    source: str
    page: int = 0
    content_type: str = "text"  # text, code, definition
    metadata: dict = field(default_factory=dict)


def create_splitter(
    chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP
) -> RecursiveCharacterTextSplitter:
    """
    Crée un text splitter configuré pour le contenu C#.

    Les séparateurs sont ordonnés pour préserver au maximum
    la cohérence des blocs de code et des paragraphes.
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n\n",  # Séparations de sections
            "\n\n",    # Séparations de paragraphes
            "\n",      # Retours ligne
            ". ",      # Phrases
            " ",       # Mots
            "",        # Caractères (dernier recours)
        ],
        length_function=len,
    )


def detect_content_type(text: str) -> str:
    """
    Détecte le type de contenu d'un chunk.

    Returns:
        "code" si le chunk contient principalement du code C#,
        "definition" si c'est une définition,
        "text" sinon.
    """
    code_indicators = [
        r"\bclass\s+\w+",
        r"\bvoid\s+\w+",
        r"\bint\s+\w+",
        r"\bstring\s+\w+",
        r"\bpublic\s+",
        r"\bprivate\s+",
        r"\bstatic\s+",
        r"\busing\s+\w+;",
        r"\bnamespace\s+",
        r"\breturn\s+",
        r"Console\.Write",
        r"\{[\s\S]*\}",
    ]

    code_score = sum(1 for pattern in code_indicators if re.search(pattern, text))
    if code_score >= 3:
        return "code"

    definition_indicators = [
        r"^(Un|Une|Le|La|Les|L')\s+\w+\s+(est|sont|permet)",
        r"^Définition\s*:",
        r"^En C#,?\s+",
    ]

    if any(re.search(p, text, re.MULTILINE) for p in definition_indicators):
        return "definition"

    return "text"


def split_document(
    text: str, source: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP
) -> list[TextChunk]:
    """
    Découpe un texte de document en chunks avec métadonnées.

    Args:
        text: Texte complet du document.
        source: Nom du fichier source.
        chunk_size: Taille cible d'un chunk.
        chunk_overlap: Chevauchement entre chunks.

    Returns:
        Liste de TextChunk.
    """
    splitter = create_splitter(chunk_size, chunk_overlap)
    raw_chunks = splitter.split_text(text)

    logger.info(
        f"Découpage de '{source}' : {len(raw_chunks)} chunks "
        f"(taille={chunk_size}, overlap={chunk_overlap})"
    )

    chunks = []
    current_page = 1

    for i, chunk_text in enumerate(raw_chunks):
        # Détecter le numéro de page à partir des marqueurs
        page_match = re.findall(r"--- Page (\d+) ---", chunk_text)
        if page_match:
            current_page = int(page_match[-1])

        # Nettoyer les marqueurs de page du texte
        clean_text = re.sub(r"\n*--- Page \d+ ---\n*", "\n", chunk_text).strip()

        if not clean_text:
            continue

        content_type = detect_content_type(clean_text)

        chunk = TextChunk(
            text=clean_text,
            chunk_id=f"{source}_{i:04d}",
            source=source,
            page=current_page,
            content_type=content_type,
            metadata={
                "char_count": len(clean_text),
                "word_count": len(clean_text.split()),
            },
        )
        chunks.append(chunk)

    logger.info(
        f"✓ '{source}' : {len(chunks)} chunks créés "
        f"(code: {sum(1 for c in chunks if c.content_type == 'code')}, "
        f"texte: {sum(1 for c in chunks if c.content_type == 'text')}, "
        f"définition: {sum(1 for c in chunks if c.content_type == 'definition')})"
    )

    return chunks
