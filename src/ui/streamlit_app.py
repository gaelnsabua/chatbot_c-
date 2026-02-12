"""
SQUAD-CSHARP - Interface Streamlit
Interface web pour le chatbot expert C#.
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from src.ingestion.vector_store import VectorStore
from src.rag.retriever import Retriever
from src.rag.prompt_builder import build_conversational_prompt, is_technical_question
from src.rag.llm_handler import LLMHandler
from src.utils.config import TOP_K_RETRIEVAL, OLLAMA_MODEL


# ============================================================
# CSS personnalisé + icônes Material Symbols
# ============================================================
CUSTOM_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet" />
<style>
    .icon-title {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .icon-subtitle {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .icon-caption {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.85rem;
        color: #888;
    }
    .material-symbols-outlined {
        font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        vertical-align: middle;
    }
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.4rem;
        font-weight: 700;
        padding: 0.5rem 0;
    }
    .sidebar-brand .material-symbols-outlined {
        font-size: 28px;
        color: #68217a;
    }
    .source-item {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 2px 0;
        font-size: 0.82rem;
        color: #666;
    }
    .source-item .material-symbols-outlined {
        font-size: 16px;
        color: #999;
    }
</style>
"""


def icon(name: str, size: int = 20) -> str:
    """Retourne le HTML d'une icône Material Symbols."""
    return f'<span class="material-symbols-outlined" style="font-size:{size}px">{name}</span>'


# ============================================================
# Configuration de la page
# ============================================================
st.set_page_config(
    page_title="SQUAD-CSHARP",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>C#</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================
# Initialisation
# ============================================================
@st.cache_resource
def init_vector_store():
    """Charge la base vectorielle (cachée entre les sessions)."""
    return VectorStore()


def create_llm():
    """Crée une nouvelle instance LLM à chaque appel."""
    return LLMHandler()


# ============================================================
# Sidebar
# ============================================================
def render_sidebar():
    """Affiche la barre latérale de configuration."""
    with st.sidebar:
        st.markdown(
            f'<div class="sidebar-brand">{icon("code", 28)} SQUAD-CSHARP</div>',
            unsafe_allow_html=True,
        )
        st.caption("Expert C# — 100% Local")

        st.divider()

        # Paramètres
        st.markdown(
            f'<div class="icon-subtitle">{icon("tune", 20)} Paramètres</div>',
            unsafe_allow_html=True,
        )
        top_k = st.slider(
            "Nombre d'extraits (top_k)",
            min_value=1,
            max_value=10,
            value=TOP_K_RETRIEVAL,
            help="Nombre de passages documentaires à récupérer",
        )

        show_sources = st.checkbox("Afficher les sources", value=True)

        st.divider()

        # Statistiques
        st.markdown(
            f'<div class="icon-subtitle">{icon("database", 20)} Base de Connaissances</div>',
            unsafe_allow_html=True,
        )
        try:
            vs = init_vector_store()
            stats = vs.get_stats()
            st.metric("Documents indexés", stats["total_documents"])
            st.caption(f"Collection : {stats['collection_name']}")
        except Exception as e:
            st.error(f"Base non disponible : {e}")

        st.divider()

        # Actions
        if st.button("Effacer la conversation", icon=":material/delete:", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.divider()
        st.markdown(
            f'<div class="icon-caption">{icon("smart_toy", 16)} Modèle : {OLLAMA_MODEL}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="icon-caption">{icon("memory", 16)} Ollama + ChromaDB</div>',
            unsafe_allow_html=True,
        )

    return top_k, show_sources


# ============================================================
# Zone de chat principale
# ============================================================
def render_chat(top_k: int, show_sources: bool):
    """Affiche et gère la zone de chat."""

    # Initialiser l'historique
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Header
    st.markdown(
        f'<div class="icon-title">{icon("code", 30)} SQUAD-CSHARP</div>',
        unsafe_allow_html=True,
    )
    st.caption("Votre assistant expert en programmation C# — 100% local et gratuit")

    # Afficher l'historique
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Afficher les sources si disponibles
            if show_sources and message.get("sources"):
                with st.expander("Sources documentaires", icon=":material/menu_book:"):
                    for src in message["sources"]:
                        st.markdown(
                            f'<div class="source-item">'
                            f'{icon("description", 16)}'
                            f'<b>{src["source"]}</b> (p.{src["page"]}) '
                            f'— distance: {src["distance"]:.4f}</div>',
                            unsafe_allow_html=True,
                        )

    # Input utilisateur
    if prompt := st.chat_input("Posez votre question sur le C#..."):
        # Afficher le message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Générer la réponse
        with st.chat_message("assistant"):
            with st.spinner("Réflexion en cours..."):
                try:
                    # 1. Récupérer le contexte (seulement si question technique)
                    docs = []
                    if is_technical_question(prompt):
                        vs = init_vector_store()
                        retriever = Retriever(vs, top_k=top_k)
                        docs = retriever.retrieve(prompt)

                    # 2. Construire le prompt
                    history = [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages[:-1]
                    ]
                    full_prompt = build_conversational_prompt(prompt, docs, history)

                    # 3. Générer la réponse (streaming)
                    llm = create_llm()
                    response_placeholder = st.empty()
                    full_response = ""

                    for token in llm.generate_stream(full_prompt):
                        full_response += token
                        response_placeholder.markdown(full_response + "▌")

                    response_placeholder.markdown(full_response)

                    # 4. Préparer les sources
                    sources = []
                    for doc in docs:
                        sources.append(
                            {
                                "source": doc["metadata"].get("source", "?"),
                                "page": doc["metadata"].get("page", "?"),
                                "distance": doc["distance"],
                            }
                        )

                    # Afficher les sources
                    if show_sources and sources:
                        with st.expander("Sources documentaires", icon=":material/menu_book:"):
                            for src in sources:
                                st.markdown(
                                    f'<div class="source-item">'
                                    f'{icon("description", 16)}'
                                    f'<b>{src["source"]}</b> (p.{src["page"]}) '
                                    f'— distance: {src["distance"]:.4f}</div>',
                                    unsafe_allow_html=True,
                                )

                    # 5. Sauvegarder dans l'historique
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": full_response,
                            "sources": sources,
                        }
                    )

                except Exception as e:
                    error_msg = (
                        f"**Erreur** : {e}\n\n"
                        "Vérifiez que :\n"
                        "1. Ollama est démarré (`ollama serve`)\n"
                        f"2. Le modèle `{OLLAMA_MODEL}` est disponible (`ollama list`)\n"
                        "3. La base de connaissances a été alimentée"
                    )
                    st.error(error_msg, icon=":material/error:")


# ============================================================
# Main
# ============================================================
def main():
    top_k, show_sources = render_sidebar()
    render_chat(top_k, show_sources)


if __name__ == "__main__":
    main()
