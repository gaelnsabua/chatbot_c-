"""
SQUAD-CSHARP - Prompt Builder
Construction des prompts contextualisés pour le LLM.
"""

import re

from src.utils.logger import logger

# Prompt système par défaut (aligné avec le Modelfile)
SYSTEM_PROMPT = """Tu es SQUAD-CSHARP, un assistant exclusivement dédié au langage de programmation C#.

RÈGLE ABSOLUE :
Tu ne réponds QU'AUX sujets liés au C# et à l'écosystème .NET. Pour TOUT autre sujet (Python, Java, cuisine, histoire, maths, etc.), tu dois refuser poliment en disant : "Je suis SQUAD-CSHARP, un assistant spécialisé uniquement en C#. Je ne peux pas t'aider sur ce sujet, mais n'hésite pas à me poser une question sur le C# !"

CONVERSATION :
- Si l'utilisateur te salue, réponds poliment et présente-toi brièvement en rappelant ta spécialisation C#.
- Si l'utilisateur te remercie, réponds courtoisement.
- Si l'utilisateur demande qui tu es, présente-toi : tu es SQUAD-CSHARP, spécialisé en C#.

RÈGLES POUR LES QUESTIONS C# :
1. Base tes réponses sur les documents fournis dans le contexte quand ils sont disponibles
2. Si l'information n'est pas dans le contexte, précise-le mais tu peux compléter avec tes connaissances en C#
3. Fournis des exemples de code C# clairs et commentés
4. Explique de manière progressive (du simple au complexe)
5. Cite tes sources (nom du document) quand le contexte documentaire est utilisé

STYLE :
- Amical et professionnel
- Pédagogique
- Précis techniquement
- En français"""


# Mots-clés indiquant une question technique
_TECHNICAL_KEYWORDS = [
    r"\bc#\b", r"\bcsharp\b", r"\bdotnet\b", r"\.net\b",
    r"\bclasse?\b", r"\binterface\b", r"\bhérit", r"\bpolymorphi",
    r"\blinq\b", r"\basync\b", r"\bawait\b", r"\btask\b",
    r"\bdelegate\b", r"\bevent\b", r"\blambda\b",
    r"\bvariable\b", r"\btype\b", r"\bstring\b", r"\bint\b", r"\bbool\b",
    r"\barray\b", r"\blist\b", r"\btableau\b", r"\bcollection\b",
    r"\bméthode\b", r"\bfonction\b", r"\bpropriété\b",
    r"\bboucle\b", r"\bcondition\b", r"\bif\b", r"\bfor\b", r"\bwhile\b",
    r"\bexception\b", r"\btry\b", r"\bcatch\b",
    r"\bnamespace\b", r"\busing\b", r"\bpublic\b", r"\bprivate\b",
    r"\bstatic\b", r"\bvoid\b", r"\breturn\b",
    r"\bconsole\b", r"\bobjet\b", r"\binstanc",
    r"\bcode\b", r"\bcompil", r"\bdébug", r"\berreur\b",
    r"\bprogramm", r"\bdévelopp", r"\balgori",
    r"\babstrai", r"\bvirtual\b", r"\boverride\b",
    r"\benum\b", r"\bstruct\b", r"\brecord\b",
    r"\bgeneric\b", r"\bgénérique\b",
    r"\bvisual\s*studio\b", r"\bnuget\b",
]


def is_technical_question(text: str) -> bool:
    """
    Détermine si le message de l'utilisateur est une question technique
    ou une simple conversation (salutation, remerciement, etc.).
    """
    text_lower = text.lower().strip()

    # Messages clairement conversationnels
    casual_patterns = [
        r"^(salut|bonjour|hello|hi|hey|coucou|bonsoir)\b",
        r"^(merci|thanks|thank you)",
        r"^(au revoir|bye|à bientôt|à\+)",
        r"^(oui|non|ok|d'accord|bien sûr)\s*[.!?]?\s*$",
        r"^(ça va|comment vas|comment tu|tu vas bien)",
        r"^(qui es[- ]tu|tu es qui|présente[- ]toi|c'est quoi ton)",
        r"^(que (fais|sais|peux)[- ]tu)",
        r"^(comment t'appelles|ton nom)",
    ]

    for pattern in casual_patterns:
        if re.search(pattern, text_lower):
            return False

    # Vérifier les mots-clés techniques
    for keyword in _TECHNICAL_KEYWORDS:
        if re.search(keyword, text_lower):
            return True

    # Messages courts sans mot-clé technique → probablement conversationnel
    if len(text_lower.split()) <= 4:
        return False

    # Par défaut, traiter comme technique (mieux vaut donner du contexte en trop)
    return True


def build_context(retrieved_docs: list[dict]) -> str:
    """
    Construit le bloc de contexte à partir des documents trouvés.

    Args:
        retrieved_docs: Liste de résultats du retriever.

    Returns:
        Texte formaté du contexte documentaire.
    """
    if not retrieved_docs:
        return "Aucun document pertinent trouvé dans la base de connaissances."

    context_parts = []
    for i, doc in enumerate(retrieved_docs):
        source = doc["metadata"].get("source", "Source inconnue")
        page = doc["metadata"].get("page", "?")
        content_type = doc["metadata"].get("content_type", "texte")

        context_parts.append(
            f"[Extrait {i + 1}] (Source: {source}, Page: {page}, Type: {content_type})\n"
            f"{doc['document']}"
        )

    return "\n\n---\n\n".join(context_parts)


def build_prompt(question: str, retrieved_docs: list[dict]) -> str:
    """
    Construit le prompt complet pour le LLM.

    Args:
        question: Question de l'utilisateur.
        retrieved_docs: Documents trouvés par le retriever.

    Returns:
        Prompt complet formaté.
    """
    # Si ce n'est pas une question technique, pas besoin du contexte documentaire
    if not is_technical_question(question):
        logger.debug(f"Message conversationnel détecté : '{question[:60]}'")
        prompt = f"""MESSAGE DE L'UTILISATEUR :
{question}

Réponds brièvement et poliment. Si c'est une salutation, présente-toi en rappelant que tu es spécialisé en C#. Si le sujet n'est pas lié au C#, refuse poliment et redirige vers le C#.

RÉPONSE :"""
        return prompt

    context = build_context(retrieved_docs)

    prompt = f"""CONTEXTE DOCUMENTAIRE :
{context}

QUESTION DE L'UTILISATEUR :
{question}

INSTRUCTIONS :
- Utilise le contexte documentaire ci-dessus pour enrichir ta réponse.
- Si l'information n'est pas dans le contexte, tu peux répondre avec tes connaissances générales mais précise-le.
- Fournis des exemples de code C# si pertinent.
- Réponds de manière structurée et pédagogique.

RÉPONSE :"""

    logger.debug(f"Prompt technique construit ({len(prompt)} caractères, {len(retrieved_docs)} extraits)")
    return prompt


def build_conversational_prompt(
    question: str, retrieved_docs: list[dict], history: list[dict] = None
) -> str:
    """
    Construit un prompt avec historique de conversation.

    Args:
        question: Question actuelle.
        retrieved_docs: Documents trouvés.
        history: Historique [{role: "user"/"assistant", content: "..."}].

    Returns:
        Prompt avec contexte conversationnel.
    """
    # Construire l'historique
    history_text = ""
    if history:
        history_parts = []
        recent_history = history[-10:]
        for msg in recent_history:
            role = "Utilisateur" if msg["role"] == "user" else "SQUAD-CSHARP"
            history_parts.append(f"{role} : {msg['content']}")
        history_text = "\n".join(history_parts)

    # Si ce n'est pas une question technique, pas besoin du contexte documentaire
    if not is_technical_question(question):
        logger.debug(f"Message conversationnel détecté : '{question[:60]}'")
        prompt = f"""{"HISTORIQUE DE CONVERSATION :" + chr(10) + history_text + chr(10) if history_text else ""}MESSAGE DE L'UTILISATEUR :
{question}

Réponds brièvement et poliment. Si c'est une salutation, présente-toi en rappelant que tu es spécialisé en C#. Si le sujet n'est pas lié au C#, refuse poliment et redirige vers le C#.

RÉPONSE :"""
        return prompt

    context = build_context(retrieved_docs)

    prompt = f"""CONTEXTE DOCUMENTAIRE :
{context}

{"HISTORIQUE DE CONVERSATION :" + chr(10) + history_text + chr(10) if history_text else ""}
QUESTION ACTUELLE DE L'UTILISATEUR :
{question}

INSTRUCTIONS :
- Utilise le contexte documentaire ci-dessus pour enrichir ta réponse.
- Tiens compte de l'historique de conversation s'il existe.
- Si l'information n'est pas dans le contexte, tu peux répondre avec tes connaissances générales mais précise-le.
- Fournis des exemples de code C# si pertinent.

RÉPONSE :"""

    return prompt
