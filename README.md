# 📊 Data Viz LLM - Version Ollama Mistral Local

**Version ultra-simplifiée - 100% GRATUITE - Aucune clé API nécessaire**

Utilise votre Mistral local via Ollama.

## ⚡ Installation (2 minutes)

### 1. Installer Ollama (si pas déjà fait)

```bash
# Linux/Mac
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: télécharger depuis ollama.ai
```

### 2. Charger Mistral

```bash
ollama pull mistral
```

### 3. Lancer Ollama

```bash
ollama serve
```

Gardez ce terminal ouvert.

### 4. Installer l'application

```bash
# Dans un nouveau terminal
pip install -r requirements.txt
```

## 🚀 Utilisation

```bash
streamlit run src/app.py
```

Ouvrir http://localhost:8501

## 📝 Utiliser Votre Modelfile

Vous avez créé `mistral-opt.txt` avec:
```
FROM mistral
PARAMETER num_gpu 10
PARAMETER num_thread 6
PARAMETER num_ctx 2048
```

**Option 1: Créer un modèle personnalisé**

```bash
# Créer le modèle
ollama create mistral-opt -f mistral-opt.txt

# Modifier src/llm/analyzer.py ligne 11:
self.model = "mistral-opt"  # Au lieu de "mistral"

# Même chose dans viz_proposer.py et code_generator.py
```

**Option 2: Utiliser directement**

Les paramètres dans votre fichier améliorent les performances:
- `num_gpu 10`: Utilise 10 GPU (si disponibles)
- `num_thread 6`: 6 threads CPU
- `num_ctx 2048`: Contexte de 2048 tokens

```bash
ollama create mistral-opt -f mistral-opt.txt
ollama run mistral-opt
```

## 🎯 Workflow

1. **Upload CSV** ou choisir un exemple
2. **Saisir question**: "Quels facteurs influencent le prix ?"
3. **Analyser** (Mistral local génère 3 propositions)
4. **Sélectionner** une visualisation
5. **Télécharger** le PNG

## ✅ Avantages

- ✅ **100% Gratuit** (pas de frais API)
- ✅ **Privé** (données restent locales)
- ✅ **Rapide** (pas de latence réseau)
- ✅ **Pas de limite** (pas de quota)

## ⚙️ Optimisation

Votre `mistral-opt.txt` optimise déjà:
- GPU: 10 cartes (si disponibles)
- Threads: 6 CPU
- Contexte: 2048 tokens

Pour créer le modèle optimisé:

```bash
ollama create mistral-opt -f mistral-opt.txt
```

Puis dans `src/llm/analyzer.py`, `viz_proposer.py`, `code_generator.py`:

```python
self.model = "mistral-opt"  
```

## 🔧 Troubleshooting

**Erreur "connection refused"**
→ Lancer `ollama serve` dans un terminal

**Réponses lentes**
→ Utiliser le modèle optimisé `mistral-opt`

**Erreur "model not found"**
→ `ollama pull mistral`

## 📁 Structure Minimale

```
src/
├── app.py              # 
├── llm/
│   ├── analyzer.py     # 
│   ├── viz_proposer.py # 
│   └── code_generator.py # 
├── utils/              # 
└── visualization/      # 
```
