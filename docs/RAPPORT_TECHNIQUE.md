# SQUAD-CSHARP : Rapport Technique de Projet

**Assistant Conversationnel Expert en C# basé sur RAG**

---

## 1. Introduction

### 1.1 Objectif du Projet

SQUAD-CSHARP est un système de question-réponse intelligent spécialisé dans l'enseignement de la programmation C#. Le projet implémente une architecture RAG (Retrieval-Augmented Generation) permettant de générer des réponses pédagogiques basées sur une documentation personnalisée, tout en fonctionnant entièrement en local.

### 1.2 Contraintes Techniques

- **Autonomie** : Fonctionnement 100% local sans connexion internet
- **Coût** : Utilisation exclusive de technologies open-source gratuites
- **Performance** : Exécution sur matériel standard (CPU uniquement, 8 Go RAM minimum)
- **Confidentialité** : Aucune donnée utilisateur transmise à des services tiers
- **Spécialisation** : Refus systématique des questions hors domaine C#/.NET

### 1.3 Architecture Générale

```
┌─────────────────────────────────────────────────────────┐
│                    SQUAD-CSHARP                         │
│                                                         │
│  Interface Utilisateur (Streamlit / CLI)                │
│           │                                             │
│           ▼                                             │
│  Détection & Filtrage (prompt_builder.py)              │
│           │                                             │
│           ├─────► Hors-sujet → Refus automatique       │
│           │                                             │
│           ├─────► Conversationnel → Réponse directe    │
│           │                                             │
│           ▼                                             │
│  Recherche RAG (retriever.py)                          │
│           │                                             │
│           ▼                                             │
│  ChromaDB (Vector Store)                               │
│           │                                             │
│           ▼                                             │
│  Génération (Ollama + SQUAD-CSHARP Model)              │
│           │                                             │
│           ▼                                             │
│  Réponse Streaming + Sources                           │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Fonctionnalités Implémentées

### 2.1 Ingestion Documentaire

✅ **Extraction PDF**
- Lecture multi-page avec PyPDF
- Extraction de métadonnées (source, numéros de page)
- Nettoyage automatique du texte (caractères spéciaux, espaces multiples)

✅ **Découpage Intelligent (Text Splitting)**
- Chunks de 1000 caractères avec overlap de 200
- Découpage basé sur des séparateurs sémantiques (paragraphes, lignes, phrases)
- Détection automatique du type de contenu :
  - `CODE` : Détection de patterns C# (class, namespace, using, etc.)
  - `DEFINITION` : Détection de patterns définitoires (est un(e), désigne, etc.)
  - `TEXT` : Texte descriptif standard

✅ **Vectorisation et Indexation**
- Transformation en embeddings via Sentence-Transformers (`all-MiniLM-L6-v2`)
- Vecteurs de 384 dimensions
- Stockage dans ChromaDB avec métadonnées enrichies
- Collection persistante `csharp_docs`

✅ **Statistiques d'Ingestion**
- Rapport détaillé : nombre de chunks, documents traités, temps d'exécution
- Logging dans fichier et console
- Mode reset pour réindexation complète

### 2.2 Système RAG (Retrieval-Augmented Generation)

✅ **Retriever (Recherche Documentaire)**
- Recherche par similarité cosinus
- Récupération des top_k documents les plus pertinents (configurable 1-10)
- Calcul et retour des distances vectorielles
- Filtrage optionnel par seuil de similarité

✅ **Prompt Builder (Construction des Prompts)**
- **Détection multi-niveau** :
  - Messages conversationnels (salutations, remerciements) → pas de RAG
  - Questions techniques C# → activation du RAG
  - Questions hors-sujet (30+ langages détectés) → refus automatique
- **Gestion du contexte** :
  - Intégration des documents récupérés
  - Historique conversationnel (10 derniers messages)
  - Adaptation du prompt selon présence/absence d'historique
- **Templates spécialisés** :
  - Prompt technique avec instructions C#-only
  - Prompt conversationnel minimaliste
  - Prompt de refus pour hors-sujet

✅ **LLM Handler (Interface Ollama)**
- Connexion au serveur Ollama local
- Génération standard et streaming
- Gestion des erreurs avec messages explicites
- Test de connexion et disponibilité du modèle

### 2.3 Interfaces Utilisateur

✅ **Interface Web (Streamlit)**
- Chat interactif avec streaming temps réel
- Sidebar de configuration :
  - Ajustement du top_k (1-10)
  - Toggle affichage des sources
  - Statistiques de la base de connaissances
- **Gestion des conversations** :
  - Création de nouvelles conversations
  - Liste de toutes les conversations avec titre auto-généré
  - Basculement entre conversations
  - Suppression de conversations
  - Sauvegarde automatique en JSON
- **Affichage enrichi** :
  - Icônes Material Symbols (sans émojis)
  - Expanders pour sources documentaires
  - Indicateurs de chargement
  - Messages d'erreur contextualisés

✅ **Interface CLI (Terminal)**
- Chat minimaliste avec Rich (coloration syntaxique)
- Commandes système : `/reset`, `/stats`, `/exit`
- Affichage compact des sources
- Logging en temps réel

### 2.4 Personnalisation du Modèle

✅ **Modelfile SQUAD-CSHARP**
- Configuration Ollama personnalisée
- System prompt C#-only avec règles strictes
- Paramètres ajustés :
  - Temperature 0.3 (réponses précises)
  - top_p 0.9, top_k 40
  - num_ctx 4096 (contexte étendu)
- **Règles de comportement** :
  - Présentation uniquement au premier message
  - Refus poli pour questions hors C#
  - Ton pédagogique et structuré
  - Pas de répétitions inutiles

### 2.5 Filtrage et Sécurité

✅ **Détection Hors-Sujet**
- Liste de 30+ langages/technologies non-C# (Java, Python, JavaScript, React, etc.)
- Vérification croisée : présence autre langage + absence de C#
- Court-circuit du RAG si hors-sujet détecté
- Prompt de refus strict sans information technique

✅ **Validation des Questions C#**
- Liste de mots-clés C# explicites (LINQ, delegate, .NET, NuGet, etc.)
- Liste de mots-clés techniques génériques (classe, boucle, variable, etc.)
- Logique de priorité : C# explicite > autre langage > technique générique

### 2.6 Utilitaires et Outils

✅ **Scripts PowerShell**
- `setup_ollama.ps1` : Installation automatique d'Ollama
  - Recherche multi-chemins (PATH, common dirs, registry)
  - Téléchargement et installation silencieuse
  - Vérification post-installation

✅ **Scripts Python**
- `ingest_pdfs.py` : Ingestion documentaire avec mode reset
- `test_connection.py` : Diagnostic complet du système
  - Test Ollama (serveur, modèle)
  - Test ChromaDB (connexion, statistiques)
  - Test embeddings (génération)

✅ **Configuration Centralisée**
- Fichier `.env` pour tous les paramètres
- Classe `Config` avec valeurs par défaut
- Validation au démarrage

✅ **Logging Multi-Niveaux**
- Console (INFO+)
- Fichier `logs/squad_csharp.log` (DEBUG+)
- Rotation automatique des logs

---

## 3. Dépendances et Modules

### 3.1 Environnement Python

**Version Requise** : Python 3.11
- Python 3.14 incompatible avec ChromaDB (Pydantic v1)
- Python 3.10 possible mais 3.11 recommandé

### 3.2 Dépendances Principales

#### LLM et Génération

```
langchain==0.3.13
langchain-ollama==0.2.1
langchain-community==0.3.13
langchain-core==0.3.28
```

**Rôle** :
- Interface avec Ollama (ChatOllama)
- Gestion des messages (SystemMessage, HumanMessage)
- Streaming de réponses

#### Découpage de Texte

```
langchain-text-splitters>=0.2.0
```

**Rôle** :
- RecursiveCharacterTextSplitter
- Découpage sémantique avec séparateurs hiérarchiques

#### Embeddings et Vectorisation

```
sentence-transformers==3.3.1
```

**Rôle** :
- Modèle `all-MiniLM-L6-v2` (384 dimensions)
- Transformation texte → vecteurs
- CPU uniquement, pas de GPU requis

#### Base de Données Vectorielle

```
chromadb==0.5.23
```

**Rôle** :
- Stockage persistant des vecteurs
- Recherche par similarité (cosine)
- Gestion des collections et métadonnées

#### Interface Web

```
streamlit==1.41.1
```

**Rôle** :
- Framework d'interface web
- Composants chat, sidebar, expanders
- Gestion du state (session_state)
- Streaming natif

#### Interface CLI

```
rich==13.9.4
```

**Rôle** :
- Coloration syntaxique
- Tables, panels, spinners
- Mise en forme élégante du terminal

#### Extraction PDF

```
PyPDF2==3.0.1
```

**Rôle** :
- Lecture de fichiers PDF
- Extraction de texte page par page
- Extraction de métadonnées

#### Utilitaires

```
python-dotenv==1.0.1
```

**Rôle** :
- Chargement des variables d'environnement depuis `.env`
- Configuration centralisée

### 3.3 Logiciels Externes

#### Ollama

**Version** : 0.1.0+
**Rôle** : Serveur local de modèles de langage
**Installation** : Via script PowerShell ou téléchargement manuel
**Configuration** : Port 11434 par défaut

#### Modèle llama3.2:3b

**Taille** : ~2 Go
**Paramètres** : 3 milliards
**Rôle** : Base pour SQUAD-CSHARP
**Installation** : `ollama pull llama3.2:3b`

---

## 4. Difficultés Rencontrées et Solutions

### 4.1 Compatibilité Python / ChromaDB

**Problème** :
```
ValueError: mismatch in version of Pydantic
AttributeError: module 'pydantic.v1' has no attribute 'BaseSettings'
```

**Cause** : Python 3.14 (novembre 2024) incompatible avec ChromaDB 0.5.x qui utilise Pydantic v1

**Solution** :
- Recréation de l'environnement virtuel avec Python 3.11 :
  ```powershell
  py -3.11 -m venv venv
  ```
- Réinstallation de toutes les dépendances
- Mise à jour de la documentation avec version précise

**Temps perdu** : ~30 minutes de debugging + réinstallation

---

### 4.2 Import LangChain Text Splitter

**Problème** :
```
ModuleNotFoundError: No module named 'langchain.text_splitter'
```

**Cause** : Refactoring de LangChain (v0.2+) - déplacement des text splitters dans un package séparé

**Solution** :
- Ajout de `langchain-text-splitters>=0.2.0` dans requirements.txt
- Modification de l'import :
  ```python
  # Ancien
  from langchain.text_splitter import RecursiveCharacterTextSplitter
  
  # Nouveau
  from langchain_text_splitters import RecursiveCharacterTextSplitter
  ```

**Temps perdu** : ~10 minutes

---

### 4.3 Ollama Non Détecté dans PATH (Windows)

**Problème** :
```
ollama : Le terme «ollama» n'est pas reconnu comme nom d'applet de commande
```

**Cause** : L'installeur Ollama (Windows) place l'exécutable dans `%LOCALAPPDATA%\Programs\Ollama\` qui n'est pas dans le PATH par défaut

**Solution** :
- Script PowerShell de détection multi-chemins :
  ```powershell
  $paths = @(
      "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe",
      "C:\Program Files\Ollama\ollama.exe",
      ...
  )
  # + recherche dans le registre Windows
  ```
- Fallback sur recherche récursive si nécessaire

**Temps perdu** : ~20 minutes pour script robuste

---

### 4.4 Erreur HTTP Client Closed (Streamlit)

**Problème** :
```
httpx.RemoteProtocolError: Server disconnected without sending a response
RuntimeError: Cannot send a request, as the client has been closed
```

**Cause** : Utilisation de `@st.cache_resource` sur LLMHandler créait une instance persistante avec un client httpx fermé après la première requête

**Solution** :
- Suppression du cache sur `create_llm()` :
  ```python
  # Ancien
  @st.cache_resource
  def create_llm():
      return LLMHandler()
  
  # Nouveau
  def create_llm():
      return LLMHandler()  # Nouvelle instance à chaque requête
  ```
- Conservation du cache uniquement sur `init_vector_store()` (sans connexion HTTP)

**Temps perdu** : ~45 minutes de debugging

---

### 4.5 Modèle Répète la Présentation à Chaque Réponse

**Problème** :
Le modèle commençait systématiquement par "Bonjour ! Je suis SQUAD-CSHARP..." même après 10 échanges

**Cause** : System prompt trop insistant + templates de prompt sans distinction historique

**Solution** :
- **System prompt** modifié avec règle claire :
  ```
  - Ne te présente que lors du TOUT PREMIER échange
  - Si un historique existe, NE TE REPRÉSENTE PAS
  ```
- **Templates** conditionnels :
  ```python
  if history_text:
      prompt += "NE TE REPRÉSENTE PAS et NE DIS PAS BONJOUR"
  else:
      prompt += "C'est le début, tu peux te présenter"
  ```
- Ajout dans style : "Va droit au but, pas de formule répétitive"

**Temps perdu** : ~30 minutes + 3 itérations de test

---

### 4.6 Modèle Répond aux Questions Hors C#

**Problème** :
Question "Comment faire une boucle en Java ?" → Réponse avec code C# au lieu d'un refus

**Cause** :
1. Détection `is_technical_question()` trop large (mots-clés génériques : "boucle", "classe", etc.)
2. Aucune détection des autres langages
3. Pas de filtrage avant le RAG

**Solution** :
- **3 listes de patterns séparées** :
  - `_CSHARP_KEYWORDS` : C#, .NET, LINQ, etc. (confirmation C#)
  - `_OTHER_LANGUAGES` : Java, Python, JavaScript, etc. (détection hors-sujet)
  - `_TECHNICAL_KEYWORDS` : Mots génériques (boucle, classe, etc.)
  
- **Fonction `is_off_topic()`** :
  ```python
  if mentions_other_language(text) and not mentions_csharp(text):
      return True  # Clairement hors-sujet
  ```
  
- **Filtrage avant RAG** :
  ```python
  if is_off_topic(prompt):
      return OFF_TOPIC_PROMPT  # Refus strict sans contexte documentaire
  ```

- **Bug regex C++** : `r"\bc\+\+\b"` ne matchait jamais
  - `\b` après `++` exige caractère alphanumérique suivant (impossible)
  - Correction : `r"\bc\+\+"` (suppression `\b` final)

**Temps perdu** : ~1 heure de refactoring + tests

---

### 4.7 Conversations Non Persistées

**Problème** :
Rechargement de Streamlit → perte de tout l'historique

**Cause** : `st.session_state` non sauvegardé sur disque

**Solution** :
- **Système de persistance JSON** :
  ```python
  data/conversations/
  ├── uuid-1.json  # {id, title, created_at, messages[]}
  ├── uuid-2.json
  └── ...
  ```
  
- **Fonctions de gestion** :
  - `load_conversation_index()` : Liste résumée
  - `load_conversation(id)` : Charge complète
  - `save_conversation(conv)` : Sauvegarde JSON
  - `sync_session_to_disk()` : Sync auto après chaque message
  
- **UI multi-conversations** :
  - Liste dans sidebar avec titre + nombre de messages
  - Bouton par conversation pour basculer
  - Bouton supprimer par conversation
  - Titre auto-généré du 1er message (50 premiers caractères)

**Temps perdu** : ~1h30 de développement + tests

---

### 4.8 Émojis dans l'Interface

**Problème** :
Demande utilisateur de retirer tous les émojis (🎯, ⚙️, 📊, etc.) et utiliser de vraies icônes

**Cause** : Utilisation d'émojis Unicode pour décoration rapide

**Solution** :
- **Google Material Symbols** via CDN :
  ```html
  <link href="https://fonts.googleapis.com/.../Material+Symbols+Outlined" />
  ```
  
- **Fonction helper** :
  ```python
  def icon(name: str, size: int = 20) -> str:
      return f'<span class="material-symbols-outlined" 
                    style="font-size:{size}px">{name}</span>'
  ```
  
- **Icônes Streamlit natives** pour composants supportés :
  ```python
  st.button("Effacer", icon=":material/delete:")
  st.expander("Sources", icon=":material/menu_book:")
  ```

**Temps perdu** : ~30 minutes de remplacement + CSS

---

## 5. Métriques du Projet

### 5.1 Volumétrie du Code

| Catégorie | Fichiers | Lignes de Code |
|-----------|----------|----------------|
| Source (src/) | 11 | ~1800 |
| Scripts | 3 | ~400 |
| Tests | 2 | ~300 |
| Configuration | 4 | ~100 |
| **TOTAL** | **20** | **~2600** |

### 5.2 Performance du Système

**Ingestion** (13 PDF de cours C#) :
- Temps total : ~2 minutes
- Chunks générés : ~3500
- Taille ChromaDB : ~150 Mo

**Requête RAG** (moyenne) :
- Recherche vectorielle : ~50-150 ms
- Génération LLM : ~3-5 secondes (streaming)
- Temps total utilisateur : 3-5 secondes

**Mémoire** :
- Ollama + modèle : ~2.5 Go RAM
- ChromaDB : ~200 Mo RAM
- Streamlit : ~150 Mo RAM
- **Total** : ~3 Go RAM utilisés

---

## 6. Tests et Validation

### 6.1 Tests Unitaires

✅ **test_ingestion.py**
- Test extraction PDF
- Test découpage en chunks
- Test détection type de contenu
- Test vectorisation

✅ **test_rag.py**
- Test recherche documentaire
- Test construction de prompts
- Test détection hors-sujet
- Test génération LLM

### 6.2 Tests Fonctionnels

✅ **Scénarios testés** :
- Conversation simple (salutation, question, remerciement)
- Questions techniques C# avec sources
- Questions hors-sujet (Java, Python, cuisine)
- Conversation multi-tours avec contexte
- Basculement entre conversations
- Suppression de conversations
- Réindexation complète

✅ **Cas limites testés** :
- Base vide (pas de PDF)
- Ollama arrêté
- Modèle manquant
- PDF corrompu
- Question vide
- Message très long (>1000 mots)

---

## 7. Conclusion

### 7.1 Objectifs Atteints

✅ Système RAG fonctionnel et stable
✅ Interface utilisateur moderne et intuitive
✅ Filtrage robuste (C#-only)
✅ Persistance des conversations
✅ Performance acceptable sur matériel standard
✅ Documentation complète (README, rapports, commentaires)

### 7.2 Points d'Amélioration Identifiés

**Court terme** :
- Export de conversations (PDF, Markdown)
- Support mode sombre
- Recherche dans l'historique

**Moyen terme** :
- Modèle plus grand (llama3.2:8b) avec GPU
- Génération de diagrammes UML
- Système de feedback utilisateur

**Long terme** :
- Extension VS Code intégrée
- Multi-utilisateurs avec base centralisée
- Fine-tuning du modèle sur corpus C# spécialisé

---

**Date** : 12 février 2026  
**Version** : 1.0  
**Lignes de code** : ~2600  
**Durée de développement** : Estimée à ~15-20 heures (hors debugging)
