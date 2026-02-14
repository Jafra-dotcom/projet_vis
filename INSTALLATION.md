# 🚀 Installation Express - 5 Minutes

## Étape 1: Ollama 

```bash
# Vérifier si Ollama est installé
ollama --version

# Si pas installé:
curl -fsSL https://ollama.ai/install.sh | sh
```

## Étape 2: 

```bash
# Télécharger Mistral
ollama pull mistral

# Créer votre modèle optimisé
ollama create mistral-opt -f mistral-opt.txt
```

Votre `mistral-opt.txt`:
```
FROM mistral
PARAMETER num_gpu 10
PARAMETER num_thread 6
PARAMETER num_ctx 2048
```

## Étape 3: Lancer Ollama 

**Terminal 1:**
```bash
ollama serve
```

Gardez ce terminal ouvert.

## Étape 4: Installer l'app 

**Terminal 2:**
```bash
pip install streamlit pandas plotly requests Pillow kaleido
```

## Étape 5: Configurer le modèle (optionnel)

Pour utiliser `mistral-opt` au lieu de `mistral`:

Éditez ces 3 fichiers (ligne 11):

**src/llm/analyzer.py:**
```python
self.model = "mistral-opt"  # Au lieu de "mistral"
```

**src/llm/viz_proposer.py:**
```python
self.model = "mistral-opt"
```

**src/llm/code_generator.py:**
```python
self.model = "mistral-opt"
```

## Étape 6: Lancer (5 secondes)

**Terminal 2:**
```bash
streamlit run src/app.py
```

Ouvrir: http://localhost:8501

## ✅ C'est Tout !

**Total: 5 minutes max**

- ✅ Pas de clé API
- ✅ Pas de compte à créer
- ✅ 100% gratuit
- ✅ 100% local

## 🎯 Test Rapide

1. Cliquer "Exemple: Immobilier"
2. Saisir: "Quels facteurs influencent le prix ?"
3. Cliquer "Analyser"
4. Sélectionner une visualisation
5. Télécharger le PNG

**Temps: 30 secondes**

---

## 🔧 Commandes Utiles

```bash
# Vérifier les modèles installés
ollama list

# Tester Mistral manuellement
ollama run mistral-opt

# Voir les logs Ollama
# (dans le terminal où tourne `ollama serve`)

# Stopper Ollama
# Ctrl+C dans le terminal ollama serve
```


