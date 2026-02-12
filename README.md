# 🎯 SQUAD-CSHARP

**Assistant Expert en Programmation C# — 100% Local & Gratuit**

Un chatbot intelligent qui répond à vos questions sur le C# en se basant sur votre propre base documentaire (PDF), sans aucune dépendance cloud.

---

## 🚀 Démarrage Rapide

### Prérequis
- **Python** 3.10+
- **Ollama** ([Télécharger](https://ollama.ai/download))

### Installation

```bash
# 1. Cloner/Ouvrir le projet
cd CHATBOT_C#

# 2. Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Copier la configuration
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/macOS

# 5. Installer Ollama et créer le modèle
.\scripts\setup_ollama.ps1   # Windows (PowerShell)
# OU manuellement :
ollama pull llama3.2:3b
cd models && ollama create SQUAD-CSHARP -f Modelfile

# 6. Placer vos PDF dans data/pdfs/
# Copiez vos cours, docs, exercices C# en format PDF

# 7. Indexer la base de connaissances
python scripts/ingest_pdfs.py

# 8. Lancer l'application
python src/main.py                  # Interface Streamlit (web)
python src/main.py --mode cli       # Interface terminal
```

---

## 📁 Structure du Projet

```
CHATBOT_C#/
├── data/
│   ├── pdfs/                  # Vos documents PDF C#
│   ├── chroma_db/             # Base vectorielle (générée)
│   └── metadata/              # Logs d'ingestion
├── src/
│   ├── ingestion/             # Chargement & indexation PDF
│   │   ├── pdf_loader.py      # Extraction de texte
│   │   ├── text_splitter.py   # Découpage en chunks
│   │   └── vector_store.py    # Gestion ChromaDB
│   ├── rag/                   # Moteur RAG
│   │   ├── retriever.py       # Recherche de similarité
│   │   ├── prompt_builder.py  # Construction des prompts
│   │   └── llm_handler.py     # Interface Ollama
│   ├── ui/                    # Interfaces utilisateur
│   │   ├── streamlit_app.py   # Interface web
│   │   └── cli_app.py         # Interface terminal
│   ├── utils/                 # Utilitaires
│   │   ├── config.py          # Configuration centralisée
│   │   ├── logger.py          # Logging
│   │   └── validators.py      # Validations
│   └── main.py                # Point d'entrée
├── models/
│   └── Modelfile              # Configuration modèle Ollama
├── scripts/
│   ├── setup_ollama.ps1       # Installation Ollama (Windows)
│   ├── ingest_pdfs.py         # Script d'ingestion
│   └── test_connection.py     # Test des composants
├── tests/                     # Tests unitaires
├── .env.example               # Template configuration
├── requirements.txt           # Dépendances Python
└── README.md                  # Ce fichier
```

---

## 🔧 Commandes Disponibles

| Commande | Description |
|----------|-------------|
| `python src/main.py` | Lance l'interface Streamlit |
| `python src/main.py --mode cli` | Lance l'interface terminal |
| `python src/main.py --ingest` | Indexe les PDF |
| `python src/main.py --test` | Teste la connexion |
| `python scripts/ingest_pdfs.py --reset` | Réindexe tout |
| `python scripts/test_connection.py` | Diagnostic complet |

---

## 📚 Ajouter des Documents

1. Placez vos fichiers PDF dans `data/pdfs/`
2. Lancez l'indexation :
   ```bash
   python scripts/ingest_pdfs.py
   # ou pour tout réindexer :
   python scripts/ingest_pdfs.py --reset
   ```

---

## ⚙️ Configuration

Éditez le fichier `.env` :

| Variable | Défaut | Description |
|----------|--------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL du serveur Ollama |
| `OLLAMA_MODEL` | `SQUAD-CSHARP` | Nom du modèle |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Modèle d'embeddings |
| `CHUNK_SIZE` | `1000` | Taille des chunks |
| `CHUNK_OVERLAP` | `200` | Chevauchement des chunks |
| `TOP_K_RETRIEVAL` | `5` | Nombre d'extraits récupérés |

---

## 🏗️ Stack Technique

| Composant | Technologie |
|-----------|-------------|
| LLM | Ollama + Llama 3.2 (3B) |
| Embeddings | Sentence-Transformers (all-MiniLM-L6-v2) |
| Vector DB | ChromaDB |
| Framework RAG | LangChain |
| Interface Web | Streamlit |
| Interface CLI | Rich |

---

## 🛠️ Dépannage

**Ollama ne répond pas**
```bash
ollama serve  # Démarrer le serveur
```

**Modèle introuvable**
```bash
ollama list   # Vérifier les modèles
cd models && ollama create SQUAD-CSHARP -f Modelfile
```

**Base de connaissances vide**
```bash
# Vérifier que des PDF sont dans data/pdfs/
python scripts/ingest_pdfs.py --reset
```

---

## 📄 Licence

MIT License — Projet éducatif
