"""
SQUAD-CSHARP - LLM Handler
Interface avec Ollama pour la génération de réponses.
"""

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

from src.rag.prompt_builder import SYSTEM_PROMPT
from src.utils.config import OLLAMA_BASE_URL, OLLAMA_MODEL, LLM_TEMPERATURE, LLM_NUM_CTX
from src.utils.logger import logger


class LLMHandler:
    """Interface avec le serveur Ollama pour la génération de texte."""

    def __init__(
        self,
        model: str = None,
        base_url: str = None,
        temperature: float = None,
        system_prompt: str = None,
    ):
        self.model = model or OLLAMA_MODEL
        self.base_url = base_url or OLLAMA_BASE_URL
        self.temperature = temperature or LLM_TEMPERATURE
        self.system_prompt = system_prompt or SYSTEM_PROMPT

        logger.info(
            f"Initialisation LLM : model={self.model}, "
            f"temperature={self.temperature}, url={self.base_url}"
        )

        self.llm = ChatOllama(
            model=self.model,
            base_url=self.base_url,
            temperature=self.temperature,
            num_ctx=LLM_NUM_CTX,
        )

    def generate(self, prompt: str) -> str:
        """
        Génère une réponse à partir d'un prompt.

        Args:
            prompt: Prompt complet (contexte + question).

        Returns:
            Texte de la réponse générée.
        """
        logger.info(f"Génération en cours (prompt: {len(prompt)} caractères)...")

        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt),
            ]

            response = self.llm.invoke(messages)
            answer = response.content

            logger.info(f"✓ Réponse générée ({len(answer)} caractères)")
            return answer

        except Exception as e:
            error_msg = f"Erreur lors de la génération : {e}"
            logger.error(error_msg)
            return (
                f"❌ Erreur de génération. Vérifiez qu'Ollama est démarré "
                f"et que le modèle '{self.model}' est disponible.\n\n"
                f"Détail : {e}"
            )

    def generate_stream(self, prompt: str):
        """
        Génère une réponse en mode streaming (pour Streamlit).

        Args:
            prompt: Prompt complet.

        Yields:
            Tokens un par un.
        """
        logger.info(f"Génération (stream) en cours...")

        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt),
            ]

            for chunk in self.llm.stream(messages):
                if chunk.content:
                    yield chunk.content

        except Exception as e:
            logger.error(f"Erreur streaming : {e}")
            yield f"\n\n❌ Erreur : {e}"

    def test_connection(self) -> bool:
        """Teste la connexion avec Ollama."""
        try:
            response = self.llm.invoke([HumanMessage(content="Réponds juste 'OK'.")])
            ok = bool(response.content)
            logger.info(f"Test connexion Ollama : {'✓' if ok else '✗'}")
            return ok
        except Exception as e:
            logger.error(f"Test connexion échoué : {e}")
            return False
