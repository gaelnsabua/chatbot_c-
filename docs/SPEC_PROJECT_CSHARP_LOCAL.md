# SQUAD-CSHARP : SPÉCIFICATION TECHNIQUE COMPLÈTE
## Assistant Conversationnel Expert C# - 100% Local & Gratuit

---

## TABLE DES MATIÈRES
1. [Vision et Objectifs](#1-vision-et-objectifs)
2. [Architecture Système](#2-architecture-système)
3. [Stack Technologique](#3-stack-technologique)
4. [Exigences Système](#4-exigences-système)
5. [Structure du Projet](#5-structure-du-projet)
6. [Pipeline d'Ingestion des Données](#6-pipeline-dingestion-des-données)
7. [Moteur RAG (Retrieval-Augmented Generation)](#7-moteur-rag)
8. [Interface Utilisateur](#8-interface-utilisateur)
9. [Fonctionnalités](#9-fonctionnalités)
10. [Configuration et Déploiement](#10-configuration-et-déploiement)
11. [Plan de Développement](#11-plan-de-développement)
12. [Tests et Validation](#12-tests-et-validation)
13. [Métriques de Performance](#13-métriques-de-performance)
14. [Maintenance et Évolution](#14-maintenance-et-évolution)

---

## 1. VISION ET OBJECTIFS

### 1.1 Vision Générale
Développer **SQUAD-CSHARP**, un assistant conversationnel intelligent expert en programmation C#, capable de répondre à des questions techniques en exploitant une base de connaissances locale issue de documents PDF (cours, documentation officielle Microsoft, tutoriels, exercices corrigés).

### 1.2 Objectifs Principaux
- ✅ **Confidentialité Absolue** : Aucune donnée ne transite par des services cloud externes
- ✅ **Coût Zéro** : Pas de frais d'API (OpenAI, Google Gemini, etc.)
- ✅ **Autonomie** : Fonctionnement hors ligne après installation initiale
- ✅ **Précision** : Réponses basées uniquement sur la documentation fournie
- ✅ **Pédagogie** : Explications claires avec exemples de code C#

### 1.3 Cas d'Usage
- Répondre à des questions sur la syntaxe C# (types, classes, interfaces, etc.)
- Expliquer des concepts avancés (LINQ, async/await, delegates, events)
- Fournir des exemples de code commentés
- Aider au débogage conceptuel
- Comparer des approches de programmation

### 1.4 Contraintes
- **Pas de connexion internet** requise en production
- **Pas d'API payante** (OpenAI, Azure, Google)
- **Ressources matérielles limitées** : Doit fonctionner sur un ordinateur standard
- **Sources de vérité** : Uniquement les documents PDF fournis

---

## 2. ARCHITECTURE SYSTÈME

### 2.1 Vue d'Ensemble
```
┌─────────────────────────────────────────────────────────────┐
│                    UTILISATEUR                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │   Interface Conversationnelle │
        │   (Streamlit / Gradio / CLI) │
        └──────────────┬───────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │   Gestionnaire de Requêtes   │
        │   (Query Handler)            │
        └──────────┬───────────────────┘
                   │
      ┌────────────┴────────────┐
      ▼                         ▼
┌─────────────┐         ┌──────────────────┐
│  ChromaDB   │◄────────│  Embeddings      │
│  (Vector DB)│         │  (all-MiniLM-L6) │
└──────┬──────┘         └──────────────────┘
       │
       │ Contexte Pertinent
       ▼
┌──────────────────────┐
│   Prompt Builder     │
│   (RAG Orchestrator) │
└──────┬───────────────┘
       │
       │ Prompt Enrichi
       ▼
┌──────────────────────┐
│   Ollama Server      │
│   (Llama 3.2 / Phi)  │
│   Modèle: SQUAD-CSHARP│
└──────┬───────────────┘
       │
       │ Réponse Générée
       ▼
┌──────────────────────┐
│   Post-Processing    │
│   (Formatting)       │
└──────┬───────────────┘
       │
       ▼
   Affichage Utilisateur
```

### 2.2 Composants Clés

#### A. Moteur d'Intelligence (LLM Local)
- **Serveur** : Ollama
- **Modèle de base** : 
  - Option 1 : `llama3.2:3b` (3 milliards de paramètres)
  - Option 2 : `phi3.5:mini` (3.8 milliards de paramètres)
- **Modèle personnalisé** : `SQUAD-CSHARP` (via Modelfile)
- **API** : REST (port 11434 par défaut)

#### B. Moteur d'Embeddings (Vectorisation)
- **Modèle** : `all-MiniLM-L6-v2` (Sentence-Transformers)
- **Dimensions** : 384
- **Taille** : ~80 MB
- **Rapidité** : ~1000 phrases/seconde (CPU)

#### C. Base de Données Vectorielle
- **Système** : ChromaDB
- **Type** : Base locale persistante
- **Distance** : Cosinus (similarité sémantique)
- **Stockage** : Fichiers locaux dans `/data/chroma_db/`

#### D. Orchestrateur RAG
- **Framework** : LangChain
- **Responsabilités** :
  - Réception de la question utilisateur
  - Vectorisation de la question
  - Recherche de similarité dans ChromaDB
  - Construction du prompt contextualisé
  - Appel à Ollama
  - Post-traitement de la réponse

---

## 3. STACK TECHNOLOGIQUE

### 3.1 Technologies Backend

| Composant | Technologie | Version | Rôle |
|-----------|-------------|---------|------|
| **Langage** | Python | 3.10+ | Langage principal |
| **LLM Server** | Ollama | Latest | Serveur de modèles locaux |
| **Modèle LLM** | Llama 3.2 / Phi-3.5 | 3B / 3.8B | Génération de texte |
| **Embeddings** | Sentence-Transformers | Latest | Vectorisation |
| **Vector DB** | ChromaDB | 0.4.22+ | Stockage vectoriel |
| **Framework RAG** | LangChain | 0.1.0+ | Orchestration RAG |
| **PDF Processing** | PyPDF / PDFPlumber | Latest | Extraction de texte |
| **Interface** | Streamlit / Gradio | Latest | UI Web |

### 3.2 Dépendances Python Complètes
```txt
# Core RAG
langchain==0.1.10
langchain-community==0.0.28
langchain-ollama==0.0.3
chromadb==0.4.22

# Embeddings
sentence-transformers==2.3.1

# PDF Processing
pypdf==4.0.1
pdfplumber==0.10.4

# Interface Utilisateur
streamlit==1.31.1
# OU
gradio==4.19.2

# Utilities
python-dotenv==1.0.1
pydantic==2.6.1
tqdm==4.66.2
```

---

## 4. EXIGENCES SYSTÈME

### 4.1 Matériel Recommandé
- **CPU** : Processeur 4 cœurs minimum (Intel i5 / AMD Ryzen 5)
- **RAM** : 8 GB minimum, 16 GB recommandé
- **Stockage** : 10 GB d'espace libre
  - Modèle Llama 3.2 (3B) : ~2 GB
  - Modèle d'embeddings : ~80 MB
  - ChromaDB + documents : ~1-5 GB
  - Dépendances Python : ~2 GB
- **GPU** : Optionnel (accélération possible avec CUDA)

### 4.2 Logiciels Requis
- **Système d'exploitation** : Windows 10/11, Linux, macOS
- **Python** : Version 3.10, 3.11 ou 3.12
- **Ollama** : Dernière version stable
- **Git** : Pour cloner le projet (optionnel)

---

## 5. STRUCTURE DU PROJET

```
CHATBOT_C#/
│
├── data/                           # Données et bases
│   ├── pdfs/                       # Documents sources
│   │   ├── cours_csharp_basics.pdf
│   │   ├── doc_microsoft_linq.pdf
│   │   └── exercices_corriges.pdf
│   │
│   ├── chroma_db/                  # Base ChromaDB (générée)
│   │   ├── chroma.sqlite3
│   │   └── ...
│   │
│   └── metadata/                   # Métadonnées d'ingestion
│       └── ingestion_log.json
│
├── src/                            # Code source
│   ├── ingestion/                  # Module d'ingestion
│   │   ├── __init__.py
│   │   ├── pdf_loader.py           # Chargement des PDF
│   │   ├── text_splitter.py        # Découpage en chunks
│   │   └── vector_store.py         # Indexation ChromaDB
│   │
│   ├── rag/                        # Module RAG
│   │   ├── __init__.py
│   │   ├── retriever.py            # Recherche de similarité
│   │   ├── prompt_builder.py       # Construction des prompts
│   │   └── llm_handler.py          # Interface avec Ollama
│   │
│   ├── ui/                         # Interface utilisateur
│   │   ├── __init__.py
│   │   ├── streamlit_app.py        # Interface Streamlit
│   │   ├── gradio_app.py           # Interface Gradio (alternative)
│   │   └── cli_app.py              # Interface CLI
│   │
│   ├── utils/                      # Utilitaires
│   │   ├── __init__.py
│   │   ├── config.py               # Configuration centralisée
│   │   ├── logger.py               # Logging
│   │   └── validators.py           # Validations
│   │
│   └── main.py                     # Point d'entrée principal
│
├── models/                         # Configurations Ollama
│   ├── Modelfile                   # Config SQUAD-CSHARP
│   └── README.md                   # Instructions création modèle
│
├── tests/                          # Tests unitaires
│   ├── test_ingestion.py
│   ├── test_rag.py
│   └── test_integration.py
│
├── docs/                           # Documentation
│   ├── SPEC_PROJECT_CSHARP_LOCAL.txt  # Ce fichier
│   ├── INSTALLATION.md             # Guide d'installation
│   ├── USAGE.md                    # Guide d'utilisation
│   └── ARCHITECTURE.md             # Documentation architecture
│
├── scripts/                        # Scripts utilitaires
│   ├── setup_ollama.sh             # Installation Ollama (Linux/Mac)
│   ├── setup_ollama.ps1            # Installation Ollama (Windows)
│   ├── ingest_pdfs.py              # Script d'ingestion standalone
│   └── test_connection.py          # Test connexion Ollama
│
├── .env.example                    # Variables d'environnement (template)
├── .gitignore                      # Fichiers ignorés par Git
├── requirements.txt                # Dépendances Python
├── README.md                       # Documentation principale
└── LICENSE                         # Licence MIT
```

---

## 6. PIPELINE D'INGESTION DES DONNÉES

### 6.1 Processus Complet

```
[PDF Files] 
    ↓
[1. Extraction] → Texte brut
    ↓
[2. Nettoyage] → Suppression artefacts
    ↓
[3. Chunking] → Segments de 1000 caractères
    ↓
[4. Vectorisation] → Vecteurs 384D
    ↓
[5. Indexation] → ChromaDB
    ↓
[Base de connaissances prête]
```

### 6.2 Étapes Détaillées

#### Étape 1 : Extraction de Texte
```python
# Utilisation de PyPDF ou PDFPlumber
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text
```

**Gestion des cas particuliers** :
- PDF scannés (OCR avec Tesseract si nécessaire)
- Encodage spécial
- Tableaux et schémas (extraction sous forme de texte structuré)

#### Étape 2 : Nettoyage
- Suppression des numéros de page
- Normalisation des espaces multiples
- Conservation des blocs de code (détection via indentation)
- Suppression des en-têtes/pieds de page répétitifs

#### Étape 3 : Découpage (Chunking)
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,           # Taille cible d'un chunk
    chunk_overlap=200,         # Chevauchement pour contexte
    separators=["\n\n", "\n", ". ", " ", ""],  # Ordre de priorité
    length_function=len
)

chunks = splitter.split_text(text)
```

**Stratégie de découpage** :
- Privilégier les coupures sur paragraphes complets
- Conserver les exemples de code entiers (détection des blocs ```csharp```)
- Ajouter des métadonnées (numéro de page source, titre de section)

#### Étape 4 : Vectorisation
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(chunks)
# Résultat : array de shape (n_chunks, 384)
```

#### Étape 5 : Indexation dans ChromaDB
```python
import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(
    persist_directory="./data/chroma_db"
))

collection = client.create_collection(
    name="csharp_knowledge",
    metadata={"description": "Documentation C#"}
)

collection.add(
    documents=chunks,
    embeddings=embeddings,
    metadatas=[{"source": pdf_name, "page": page_num} for ...],
    ids=[f"doc_{i}" for i in range(len(chunks))]
)
```

### 6.3 Métadonnées Conservées
Pour chaque chunk :
- `source` : Nom du fichier PDF source
- `page` : Numéro de page d'origine
- `chunk_id` : Identifiant unique
- `date_ingestion` : Timestamp d'indexation
- `type_content` : "texte", "code", "exemple", "définition"

---

## 7. MOTEUR RAG (RETRIEVAL-AUGMENTED GENERATION)

### 7.1 Workflow Complet

```
Question Utilisateur
    ↓
[Vectorisation de la question]
    ↓
[Recherche dans ChromaDB] → Top 5 chunks pertinents
    ↓
[Construction du prompt]
    ↓
System Prompt + Contexte + Question
    ↓
[Envoi à Ollama SQUAD-CSHARP]
    ↓
[Génération de la réponse]
    ↓
[Post-traitement]
    ↓
Affichage à l'utilisateur
```

### 7.2 Recherche de Similarité

```python
def retrieve_context(question: str, top_k: int = 5):
    # Vectorisation de la question
    question_embedding = embedding_model.encode([question])[0]
    
    # Recherche dans ChromaDB
    results = collection.query(
        query_embeddings=[question_embedding.tolist()],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    
    return results
```

**Paramètres optimaux** :
- `top_k = 5` : Nombre de chunks retournés
- Seuil de distance : 0.7 (cosinus similarity)
- Ré-ranking optionnel : Par pertinence de page source

### 7.3 Construction du Prompt

```python
def build_prompt(question: str, context_chunks: list) -> str:
    context = "\n\n---\n\n".join([
        f"[Extrait {i+1}] (Source: {chunk['metadata']['source']})\n{chunk['document']}"
        for i, chunk in enumerate(context_chunks)
    ])
    
    prompt = f"""Tu es SQUAD-CSHARP, un expert en programmation C#.

CONTEXTE DOCUMENTAIRE :
{context}

QUESTION DE L'UTILISATEUR :
{question}

INSTRUCTIONS :
- Base ta réponse UNIQUEMENT sur le contexte fourni ci-dessus
- Si l'information n'est pas dans le contexte, dis-le clairement
- Fournis des exemples de code C# si pertinent
- Explique de manière pédagogique et structurée

RÉPONSE :"""
    
    return prompt
```

### 7.4 Appel à Ollama

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="SQUAD-CSHARP",  # Notre modèle personnalisé
    temperature=0.3,       # Réponses plus déterministes
    base_url="http://localhost:11434"
)

response = llm.invoke(prompt)
```

### 7.5 Post-Traitement
- Formatage du code (coloration syntaxique)
- Ajout des références (sources documentaires)
- Vérification de cohérence
- Limitation de longueur si nécessaire

---

## 8. INTERFACE UTILISATEUR

### 8.1 Option 1 : Streamlit (Recommandée)

**Caractéristiques** :
- Interface web moderne
- Déploiement local simple
- Historique de conversation
- Affichage markdown/code natif

**Fonctionnalités** :
- Chat interactif
- Upload de nouveaux PDF
- Paramètres ajustables (température, top_k)
- Export des conversations

### 8.2 Option 2 : Gradio

**Avantages** :
- Interface plus simple
- API de partage temporaire
- Composants prédéfinis

### 8.3 Option 3 : CLI (Command Line Interface)

**Usage** :
```bash
python src/ui/cli_app.py --question "Comment utiliser LINQ?"
```

**Mode interactif** :
```bash
python src/ui/cli_app.py --interactive
```

---

## 9. FONCTIONNALITÉS

### 9.1 Fonctionnalités Core (MVP)
- ✅ Réponse à des questions sur le C#
- ✅ Recherche dans la base documentaire
- ✅ Génération de réponses contextualisées
- ✅ Fourniture d'exemples de code
- ✅ Références aux sources documentaires

### 9.2 Fonctionnalités Avancées (Phase 2)
- 🔄 Historique de conversation persistant
- 🔄 Gestion de contexte multi-tours (follow-up questions)
- 🔄 Export des réponses (Markdown, PDF)
- 🔄 Ajout dynamique de nouveaux documents
- 🔄 Statistiques d'utilisation

### 9.3 Fonctionnalités Futures (Phase 3)
- 🚀 Support de code multi-langages (VB.NET, F#)
- 🚀 Analyse de code utilisateur
- 🚀 Suggestions d'amélioration
- 🚀 Quiz interactifs
- 🚀 Génération de projets C# complets

---

## 10. CONFIGURATION ET DÉPLOIEMENT

### 10.1 Installation Ollama

**Windows** :
```powershell
# Télécharger depuis https://ollama.ai/download
# Installer l'exécutable
# Vérifier l'installation
ollama --version
```

**Linux/macOS** :
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 10.2 Téléchargement du Modèle de Base
```bash
ollama pull llama3.2:3b
# OU
ollama pull phi3.5:mini
```

### 10.3 Création du Modèle Personnalisé

**Fichier `models/Modelfile`** :
```dockerfile
FROM llama3.2:3b

# Paramètres du modèle
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 4096

# Identité et comportement
SYSTEM """Tu es SQUAD-CSHARP, un assistant expert en programmation C# développé pour aider les développeurs et étudiants.

RÈGLES FONDAMENTALES :
1. Base tes réponses UNIQUEMENT sur les documents fournis dans le contexte
2. Si une information n'est pas dans le contexte, dis explicitement : "Cette information n'est pas présente dans ma base de connaissance actuelle"
3. Fournis des exemples de code C# clairs et commentés
4. Explique les concepts de manière progressive (du simple au complexe)
5. Cite tes sources (nom du document) quand c'est pertinent

STRUCTURE DE RÉPONSE IDÉALE :
- Introduction concise
- Explication détaillée
- Exemple de code (si applicable)
- Bonnes pratiques
- Référence documentaire

STYLE :
- Professionnel mais accessible
- Pédagogique
- Précis techniquement
- En français
"""
```

**Création** :
```bash
cd models
ollama create SQUAD-CSHARP -f Modelfile
```

**Vérification** :
```bash
ollama list
# Devrait afficher SQUAD-CSHARP dans la liste
```

### 10.4 Installation des Dépendances Python

```bash
# Création environnement virtuel
python -m venv venv

# Activation
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Installation dépendances
pip install -r requirements.txt
```

### 10.5 Configuration Environnement

**Fichier `.env`** :
```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=SQUAD-CSHARP

# Embeddings Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=./data/chroma_db
CHROMA_COLLECTION_NAME=csharp_knowledge

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=5

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/squad_csharp.log
```

### 10.6 Ingestion Initiale des Documents

```bash
python scripts/ingest_pdfs.py --pdf-dir ./data/pdfs --reset
```

Options :
- `--pdf-dir` : Dossier contenant les PDF
- `--reset` : Réinitialiser la base ChromaDB
- `--batch-size` : Nombre de chunks par batch (défaut: 100)

---

## 11. PLAN DE DÉVELOPPEMENT

### Phase 1 : Fondations (Semaines 1-2)
- [x] Rédaction spécifications
- [ ] Setup environnement de développement
- [ ] Installation Ollama + modèle de base
- [ ] Création du Modelfile SQUAD-CSHARP
- [ ] Structure de projet complète
- [ ] Module d'extraction PDF (basique)

### Phase 2 : Pipeline d'Ingestion (Semaines 3-4)
- [ ] Développement module de chunking intelligent
- [ ] Intégration Sentence-Transformers
- [ ] Implémentation ChromaDB
- [ ] Scripts d'ingestion automatique
- [ ] Gestion des métadonnées
- [ ] Tests d'ingestion sur 3 PDF témoins

### Phase 3 : Moteur RAG (Semaines 5-6)
- [ ] Module de recherche vectorielle
- [ ] Prompt builder dynamique
- [ ] Interface avec Ollama
- [ ] Gestion du contexte conversationnel
- [ ] Post-traitement des réponses
- [ ] Tests unitaires RAG

### Phase 4 : Interface Utilisateur (Semaine 7)
- [ ] Interface Streamlit MVP
- [ ] Design UI/UX moderne
- [ ] Historique de conversation
- [ ] Display des sources
- [ ] Tests utilisateur

### Phase 5 : Optimisation (Semaine 8)
- [ ] Tuning des paramètres RAG (top_k, temperature)
- [ ] Amélioration du chunking (détection code)
- [ ] Cache des embeddings
- [ ] Optimisation performances
- [ ] Documentation utilisateur

### Phase 6 : Déploiement et Documentation (Semaine 9)
- [ ] Guide d'installation complet
- [ ] Documentation API
- [ ] Vidéo démo
- [ ] Package de distribution
- [ ] Tests finaux

---

## 12. TESTS ET VALIDATION

### 12.1 Tests Unitaires

**Module Ingestion** :
- Test d'extraction PDF
- Test de chunking (tailles, overlaps)
- Test d'indexation ChromaDB

**Module RAG** :
- Test de recherche vectorielle
- Test de construction de prompt
- Test d'appel Ollama

### 12.2 Tests d'Intégration
- Pipeline complet : Question → Réponse
- Gestion de multiples tours de conversation
- Performance sur batch de questions

### 12.3 Tests de Qualité (Quality Assurance)

**Jeu de test (20 questions)** :
1. Questions simples (syntaxe de base)
2. Questions complexes (async/await, LINQ)
3. Questions pièges (hors contexte documentaire)
4. Questions ambiguës

**Critères d'évaluation** :
- Pertinence de la réponse (1-5)
- Précision technique (1-5)
- Complétude (1-5)
- Fourniture d'exemples (Oui/Non)
- Citation des sources (Oui/Non)

**Objectif** : Score moyen ≥ 4/5

---

## 13. MÉTRIQUES DE PERFORMANCE

### 13.1 Métriques Techniques
- **Temps de réponse** : < 10 secondes (CPU)
- **Temps d'ingestion** : < 5 min pour 100 pages
- **Utilisation RAM** : < 4 GB
- **Précision retrieval** : Top-5 contient la réponse dans 80% des cas

### 13.2 Métriques Utilisateur
- **Satisfaction** : Enquête post-utilisation (1-5)
- **Taux de réussite** : Question résolue sans recherche externe
- **Engagement** : Nombre de questions par session

---

## 14. MAINTENANCE ET ÉVOLUTION

### 14.1 Mise à Jour de la Base de Connaissances
```bash
# Ajout de nouveaux PDF
python scripts/ingest_pdfs.py --pdf-dir ./data/pdfs/new --incremental

# Réindexation complète
python scripts/ingest_pdfs.py --pdf-dir ./data/pdfs --reset
```

### 14.2 Mise à Jour du Modèle LLM
```bash
# Mettre à jour le modèle de base
ollama pull llama3.2:latest

# Re-créer le modèle personnalisé
cd models
ollama create SQUAD-CSHARP -f Modelfile --force
```

### 14.3 Amélioration Continue
- Collecte de feedback utilisateur
- Analyse des questions sans réponse satisfaisante
- Enrichissement de la base documentaire
- Fine-tuning des paramètres RAG

---

## ANNEXES

### A. Commandes Utiles

**Gestion Ollama** :
```bash
# Lister les modèles
ollama list

# Supprimer un modèle
ollama rm SQUAD-CSHARP

# Tester un modèle
ollama run SQUAD-CSHARP "Bonjour, qui es-tu ?"
```

**Gestion ChromaDB** :
```python
# Réinitialiser la base
import chromadb
client = chromadb.Client(Settings(persist_directory="./data/chroma_db"))
client.delete_collection("csharp_knowledge")
```

### B. Résolution de Problèmes

**Ollama ne démarre pas** :
- Vérifier que le port 11434 n'est pas utilisé
- Redémarrer le service Ollama

**Embeddings trop lents** :
- Utiliser un modèle plus petit (all-MiniLM-L12-v2 → L6-v2)
- Activer CUDA si GPU disponible

**Réponses hors contexte** :
- Diminuer la température (0.3 → 0.1)
- Augmenter le nombre de chunks récupérés (5 → 8)
- Améliorer le prompt système

---

## CONCLUSION

Cette spécification définit un système RAG complet, local et gratuit pour créer un assistant expert en C#. L'approche modulaire permet une implémentation progressive et des améliorations itératives.

**Points forts** :
✅ Indépendance totale (Cloud-free)
✅ Coût nul
✅ Confidentialité préservée
✅ Extensible et maintenable

**Prochaines étapes** :
1. Valider cette spécification
2. Démarrer la Phase 1 (Setup)
3. Itérer sur MVP
4. Collecter feedback utilisateur

---

**Version** : 1.0  
**Date** : 11 Février 2026  
**Auteur** : Équipe SQUAD-CSHARP  
**Statut** : ✅ Spécification Validée
