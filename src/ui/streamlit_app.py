"""
SQUAD-CSHARP - Interface Streamlit
Interface web pour le chatbot expert C#.
"""

import sys
import json
import uuid
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire racine au path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from src.ingestion.vector_store import VectorStore
from src.rag.retriever import Retriever
from src.rag.prompt_builder import build_conversational_prompt, is_technical_question, is_off_topic
from src.rag.llm_handler import LLMHandler
from src.utils.config import TOP_K_RETRIEVAL, OLLAMA_MODEL

# ============================================================
# Fichier de persistance des conversations
# ============================================================
CONVERSATIONS_DIR = ROOT_DIR / "data" / "conversations"
CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Gestion des conversations
# ============================================================
def _conv_path(conv_id: str) -> Path:
    """Chemin du fichier JSON d'une conversation."""
    return CONVERSATIONS_DIR / f"{conv_id}.json"


def load_conversation_index() -> list[dict]:
    """Charge la liste résumée de toutes les conversations (id, title, date).
    Triées par date décroissante (la plus récente en premier)."""
    convs = []
    for f in CONVERSATIONS_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            convs.append({
                "id": data["id"],
                "title": data["title"],
                "created_at": data["created_at"],
                "message_count": len(data.get("messages", [])),
            })
        except Exception:
            continue
    convs.sort(key=lambda c: c["created_at"], reverse=True)
    return convs


def load_conversation(conv_id: str) -> dict | None:
    """Charge une conversation complète depuis le disque."""
    path = _conv_path(conv_id)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def save_conversation(conv: dict) -> None:
    """Sauvegarde une conversation sur le disque."""
    path = _conv_path(conv["id"])
    path.write_text(json.dumps(conv, ensure_ascii=False, indent=2), encoding="utf-8")


def create_new_conversation() -> dict:
    """Crée une nouvelle conversation vide."""
    conv = {
        "id": str(uuid.uuid4()),
        "title": "Nouvelle conversation",
        "created_at": datetime.now().isoformat(),
        "messages": [],
    }
    save_conversation(conv)
    return conv


def delete_conversation(conv_id: str) -> None:
    """Supprime une conversation du disque."""
    path = _conv_path(conv_id)
    if path.exists():
        path.unlink()


def generate_title(first_message: str) -> str:
    """Génère un titre court à partir du premier message utilisateur."""
    title = first_message.strip().replace("\n", " ")
    if len(title) > 50:
        title = title[:47] + "..."
    return title


def sync_session_to_disk() -> None:
    """Synchronise la conversation en cours (session_state) vers le disque."""
    conv_id = st.session_state.get("current_conv_id")
    if not conv_id:
        return
    conv = load_conversation(conv_id)
    if conv is None:
        return
    conv["messages"] = st.session_state.messages
    # Mettre à jour le titre si premier message utilisateur
    user_msgs = [m for m in conv["messages"] if m["role"] == "user"]
    if user_msgs and conv["title"] == "Nouvelle conversation":
        conv["title"] = generate_title(user_msgs[0]["content"])
    save_conversation(conv)


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
    /* --- Historique des conversations --- */
    .conv-list {
        display: flex;
        flex-direction: column;
        gap: 2px;
        max-height: 300px;
        overflow-y: auto;
        padding-right: 4px;
    }
    .conv-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 7px 10px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 0.82rem;
        color: #ccc;
        transition: background 0.15s;
    }
    .conv-item:hover {
        background: rgba(255,255,255,0.06);
    }
    .conv-item.active {
        background: rgba(104,33,122,0.18);
        color: #fff;
        font-weight: 600;
    }
    .conv-item .material-symbols-outlined {
        font-size: 16px;
        flex-shrink: 0;
    }
    .conv-title {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        flex: 1;
    }
    .conv-date {
        font-size: 0.7rem;
        color: #777;
        flex-shrink: 0;
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


def init_session_state():
    """Initialise l'état de la session avec une conversation."""
    if "current_conv_id" not in st.session_state:
        # Charger la dernière conversation ou en créer une nouvelle
        index = load_conversation_index()
        if index:
            conv = load_conversation(index[0]["id"])
            st.session_state.current_conv_id = conv["id"]
            st.session_state.messages = conv.get("messages", [])
        else:
            conv = create_new_conversation()
            st.session_state.current_conv_id = conv["id"]
            st.session_state.messages = []

    if "messages" not in st.session_state:
        st.session_state.messages = []


def switch_conversation(conv_id: str):
    """Bascule vers une autre conversation."""
    # Sauvegarder la conversation actuelle d'abord
    sync_session_to_disk()
    # Charger la nouvelle
    conv = load_conversation(conv_id)
    if conv:
        st.session_state.current_conv_id = conv["id"]
        st.session_state.messages = conv.get("messages", [])


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

        # ---- Historique des conversations ----
        st.markdown(
            f'<div class="icon-subtitle">{icon("forum", 20)} Conversations</div>',
            unsafe_allow_html=True,
        )

        # Bouton nouvelle conversation
        if st.button(
            "Nouvelle conversation",
            icon=":material/add_comment:",
            use_container_width=True,
        ):
            sync_session_to_disk()
            conv = create_new_conversation()
            st.session_state.current_conv_id = conv["id"]
            st.session_state.messages = []
            st.rerun()

        # Liste des conversations
        conv_index = load_conversation_index()
        current_id = st.session_state.get("current_conv_id", "")

        if conv_index:
            for conv_info in conv_index:
                cid = conv_info["id"]
                is_active = cid == current_id
                title = conv_info["title"]
                msg_count = conv_info["message_count"]
                try:
                    dt = datetime.fromisoformat(conv_info["created_at"])
                    date_label = dt.strftime("%d/%m %H:%M")
                except Exception:
                    date_label = ""

                # Deux colonnes : bouton conversation + bouton supprimer
                col_conv, col_del = st.columns([6, 1])

                with col_conv:
                    btn_type = "primary" if is_active else "secondary"
                    label = f"{title}  ({msg_count} msg)"
                    if st.button(
                        label,
                        key=f"conv_{cid}",
                        use_container_width=True,
                        type=btn_type,
                    ):
                        if not is_active:
                            switch_conversation(cid)
                            st.rerun()

                with col_del:
                    if st.button(
                        "",
                        key=f"del_{cid}",
                        icon=":material/close:",
                    ):
                        delete_conversation(cid)
                        # Si on supprime la conversation active, en charger une autre
                        if is_active:
                            remaining = [c for c in conv_index if c["id"] != cid]
                            if remaining:
                                switch_conversation(remaining[0]["id"])
                            else:
                                conv = create_new_conversation()
                                st.session_state.current_conv_id = conv["id"]
                                st.session_state.messages = []
                        st.rerun()
        else:
            st.caption("Aucune conversation")

        st.divider()

        # ---- Paramètres ----
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
            # Réinitialiser le titre de la conversation
            conv = load_conversation(st.session_state.current_conv_id)
            if conv:
                conv["messages"] = []
                conv["title"] = "Nouvelle conversation"
                save_conversation(conv)
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
        sync_session_to_disk()
        with st.chat_message("user"):
            st.markdown(prompt)

        # Générer la réponse
        with st.chat_message("assistant"):
            with st.spinner("Réflexion en cours..."):
                try:
                    # 1. Récupérer le contexte (seulement si question technique C#)
                    docs = []
                    if is_technical_question(prompt) and not is_off_topic(prompt):
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

                    # 6. Persister sur disque
                    sync_session_to_disk()

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
    init_session_state()
    top_k, show_sources = render_sidebar()
    render_chat(top_k, show_sources)


if __name__ == "__main__":
    main()
