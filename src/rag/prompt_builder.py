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
- Ne te présente que lors du TOUT PREMIER échange. Si un historique de conversation existe, NE TE REPRÉSENTE PAS et NE DIS PAS BONJOUR à nouveau.
- Si l'utilisateur te salue ET qu'il n'y a PAS d'historique, réponds poliment et présente-toi brièvement.
- Si l'utilisateur te salue ET qu'il y a DÉJÀ un historique, réponds simplement (ex : "Oui ?", "Je t'écoute !", "Comment puis-je t'aider ?") sans te représenter.
- Si l'utilisateur te remercie, réponds courtoisement en une phrase.
- Si l'utilisateur demande qui tu es, présente-toi.
- Ne répète JAMAIS la même information d'une réponse à l'autre.

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
- Va droit au but, pas de formule de politesse répétitive
- En français"""

# Prompt de refus pour questions hors-sujet (autre langage, sujet non-C#)
_OFF_TOPIC_PROMPT = """L'utilisateur a posé cette question :
{question}

Cette question ne concerne PAS le C# ou l'écosystème .NET.
Tu DOIS refuser de répondre. Dis poliment que tu es spécialisé uniquement en C# et que tu ne peux pas aider sur ce sujet. Propose de répondre à une question sur le C#.
Ne donne AUCUNE explication, AUCUN code, AUCUNE information sur le sujet demandé.

RÉPONSE :"""


# Langages/technologies NON-C# : si l'un de ces mots apparaît
# et que le message ne mentionne PAS C#/.NET, c'est hors-sujet.
_OTHER_LANGUAGES = [
    r"\bjava\b", r"\bjavascript\b", r"\bjs\b", r"\btypescript\b", r"\bts\b",
    r"\bpython\b", r"\bruby\b", r"\brust\b", r"\bgo\b", r"\bgolang\b",
    r"\bphp\b", r"\bswift\b", r"\bkotlin\b", r"\bscala\b", r"\bperl\b",
    r"\bc\+\+", r"\bcpp\b", r"\bobjective.?c\b",
    r"\bhtml\b", r"\bcss\b", r"\bsql\b", r"\bbash\b", r"\bshell\b",
    r"\breact\b", r"\bangular\b", r"\bvue\b", r"\bdjango\b", r"\bflask\b",
    r"\bspring\b", r"\blaravel\b", r"\bnodejs\b", r"\bnode\.js\b",
    r"\bdart\b", r"\bflutter\b", r"\belixir\b", r"\bhaskell\b",
    r"\bmatlab\b", r"\br\b(?=\s+language|\s+programming|\s+studio)",
    r"\blua\b", r"\bzig\b", r"\bcobol\b", r"\bfortran\b",
]

# Mots-clés confirmant que la question porte sur C# / .NET
_CSHARP_KEYWORDS = [
    r"\bc#\b", r"\bcsharp\b", r"\bc\s*sharp\b",
    r"\bdotnet\b", r"\.net\b", r"\basp\.?net\b",
    r"\blinq\b", r"\bdelegate\b", r"\bnuget\b",
    r"\bvisual\s*studio\b", r"\bxaml\b", r"\bwpf\b", r"\bwinforms\b",
    r"\bunity\b", r"\bmaui\b", r"\bblazor\b", r"\brazor\b",
    r"\bentity\s*framework\b", r"\bef\s*core\b",
]

# Mots-clés indiquant une question technique (générique programmation)
_TECHNICAL_KEYWORDS = [
    r"\bclasse?\b", r"\binterface\b", r"\bhérit", r"\bpolymorphi",
    r"\basync\b", r"\bawait\b", r"\btask\b",
    r"\bevent\b", r"\blambda\b",
    r"\bvariable\b", r"\btype\b", r"\bstring\b", r"\bint\b", r"\bbool\b",
    r"\barray\b", r"\blist\b", r"\btableau\b", r"\bcollection\b",
    r"\bméthode\b", r"\bfonction\b", r"\bpropriété\b",
    r"\bboucle\b", r"\bcondition\b",
    r"\bexception\b", r"\btry\b", r"\bcatch\b",
    r"\bnamespace\b", r"\busing\b",
    r"\bconsole\b", r"\bobjet\b", r"\binstanc",
    r"\bcode\b", r"\bcompil", r"\bdébug", r"\berreur\b",
    r"\bprogramm", r"\bdévelopp", r"\balgori",
    r"\babstrai", r"\bvirtual\b", r"\boverride\b",
    r"\benum\b", r"\bstruct\b", r"\brecord\b",
    r"\bgeneric\b", r"\bgénérique\b",
]


def _mentions_other_language(text: str) -> bool:
    """Vérifie si le texte mentionne un langage/techno autre que C#."""
    text_lower = text.lower()
    for pattern in _OTHER_LANGUAGES:
        if re.search(pattern, text_lower):
            return True
    return False


def _mentions_csharp(text: str) -> bool:
    """Vérifie si le texte mentionne explicitement C# / .NET."""
    text_lower = text.lower()
    for pattern in _CSHARP_KEYWORDS:
        if re.search(pattern, text_lower):
            return True
    return False


def is_off_topic(text: str) -> bool:
    """
    Détecte si la question porte sur un autre langage que C#.
    Retourne True si le message mentionne un autre langage
    SANS mentionner C# (= clairement hors-sujet).
    """
    if _mentions_other_language(text) and not _mentions_csharp(text):
        return True
    return False


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

    # Si la question mentionne C# explicitement → technique C#
    if _mentions_csharp(text):
        return True

    # Si la question mentionne un AUTRE langage (sans C#) → hors sujet, pas technique C#
    if _mentions_other_language(text):
        return False

    # Vérifier les mots-clés techniques génériques
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
    # Détection de question hors-sujet (autre langage que C#)
    if is_off_topic(question):
        logger.debug(f"Question hors-sujet détectée : '{question[:60]}'")
        return _OFF_TOPIC_PROMPT.format(question=question)

    # Si ce n'est pas une question technique, pas besoin du contexte documentaire
    if not is_technical_question(question):
        logger.debug(f"Message conversationnel détecté : '{question[:60]}'")
        prompt = f"""MESSAGE DE L'UTILISATEUR :
{question}

Réponds brièvement et poliment. Si le sujet n'est pas lié au C#, refuse poliment et redirige vers le C#.

RÉPONSE :"""
        return prompt

    context = build_context(retrieved_docs)

    prompt = f"""CONTEXTE DOCUMENTAIRE :
{context}

QUESTION DE L'UTILISATEUR :
{question}

INSTRUCTIONS :
- Tu ne réponds QU'AUX questions sur le C# et .NET. Si la question concerne un autre langage, refuse poliment.
- Utilise le contexte documentaire ci-dessus pour enrichir ta réponse.
- Si l'information n'est pas dans le contexte, tu peux répondre avec tes connaissances en C# mais précise-le.
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

    # Détection de question hors-sujet (autre langage que C#)
    if is_off_topic(question):
        logger.debug(f"Question hors-sujet détectée : '{question[:60]}'")
        return _OFF_TOPIC_PROMPT.format(question=question)

    # Si ce n'est pas une question technique, pas besoin du contexte documentaire
    if not is_technical_question(question):
        logger.debug(f"Message conversationnel détecté : '{question[:60]}'")
        if history_text:
            prompt = f"""HISTORIQUE DE CONVERSATION :
{history_text}

MESSAGE DE L'UTILISATEUR :
{question}

IMPORTANT : Un historique existe, donc NE TE REPRÉSENTE PAS et NE DIS PAS BONJOUR. Réponds directement et brièvement. Si le sujet n'est pas lié au C#, refuse poliment.

RÉPONSE :"""
        else:
            prompt = f"""MESSAGE DE L'UTILISATEUR :
{question}

C'est le début de la conversation. Si c'est une salutation, tu peux te présenter brièvement. Si le sujet n'est pas lié au C#, refuse poliment et redirige vers le C#.

RÉPONSE :"""
        return prompt

    context = build_context(retrieved_docs)

    history_block = ""
    if history_text:
        history_block = f"""HISTORIQUE DE CONVERSATION :
{history_text}

"""

    prompt = f"""CONTEXTE DOCUMENTAIRE :
{context}

{history_block}QUESTION ACTUELLE DE L'UTILISATEUR :
{question}

INSTRUCTIONS :
- IMPORTANT : Tu ne réponds QU'AUX questions sur le C# et .NET. Si la question concerne un autre langage ou un sujet hors C#, refuse poliment.
- Réponds directement à la question, sans te présenter ni dire bonjour.
- Utilise le contexte documentaire ci-dessus pour enrichir ta réponse.
- Tiens compte de l'historique de conversation s'il existe.
- Si l'information n'est pas dans le contexte, tu peux répondre avec tes connaissances en C# mais précise-le.
- Fournis des exemples de code C# si pertinent.

RÉPONSE :"""

    return prompt
