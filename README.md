# 🤖 AI Agents Code Interpreter

> **Objectif** : Construire des Agents IA Hiérarchiques capables d'exécuter du code Python et d'analyser des fichiers CSV.

## 📚 Structure du Projet

Ce repo est structuré en deux parties pédagogiques :

### 1. `agents_basics/` - Comprendre les fondamentaux

Implémentation avec **LangChain AgentExecutor** (approche "classique") pour comprendre :
- Le pattern **ReAct** (Reasoning + Acting)
- Comment les tools sont invoqués
- Les limites de cette approche (contrôle limité, debugging difficile)

### 2. `agents_advanced/` - Production-ready avec LangGraph

Refonte moderne avec **LangGraph** pour avoir :
- Un contrôle explicite sur le flow (state machine)
- Une meilleure observabilité
- La possibilité d'implémenter des patterns avancés (human-in-the-loop, routing hiérarchique)

## 🚀 Installation

```bash
# Clone le repo
git clone <repo-url>
cd ai-agents-code-interpreter

# Install avec uv (recommandé)
uv sync

# Copie le fichier d'environnement
cp .env.example .env
# Édite .env avec ta clé OpenAI
```

## 🔧 Configuration

Crée un fichier `.env` à la racine :

```env
OPENAI_API_KEY=sk-your-key-here

# Optionnel mais recommandé pour le debugging
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2-your-key-here
LANGCHAIN_PROJECT=ai-agents-code-interpreter
```

## 📖 Ordre d'apprentissage recommandé

1. **`agents_basics/01_react_agent.py`** - Comprendre le pattern ReAct
2. **`agents_basics/02_tools_custom.py`** - Créer ses propres tools
3. **`agents_basics/03_python_repl.py`** - Code Interpreter basique
4. **`agents_advanced/`** - Refonte complète avec LangGraph

## 🛠️ Commandes utiles

```bash
# Lancer un script
uv run python agents_basics/01_react_agent.py

# Lancer le linter
uv run ruff check .

# Formatter le code
uv run ruff format .

# Lancer Jupyter
uv run jupyter notebook
```

## 📝 Notes

- **Python 3.12+** requis
- Utilise `uv` pour la gestion des dépendances (moderne, rapide)
- Configuration `ruff` incluse pour le linting/formatting

