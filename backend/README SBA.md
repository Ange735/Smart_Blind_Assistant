# Smart Blind Assistant — Backend

Assistant intelligent pour malvoyants — Backend FastAPI + Computer Vision + NLP

---

## Prérequis

- Python 3.10+
- pip
- Git

---

## Installation

### 1. Cloner le projet et se placer dans le backend

```bash
git clone <repo>
cd Smart_Blind_Assistant/backend
```

### 2. Créer et activer l'environnement virtuel

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

Si `requirements.txt` n'existe pas encore :

```bash
pip install fastapi uvicorn python-multipart
pip install ultralytics
pip install transformers torch pillow
pip install sentence-transformers scikit-learn
pip install spacy
python -m spacy download fr_core_news_sm
pip install streamlit requests
pip install opencv-python numpy
```

---

## Structure des fichiers

```
backend/
├── main.py                          ← API REST principale
├── demo.py                          ← Pipeline de démonstration (port 8001)
├── caregiver.py                     ← Interface Streamlit aidant
│
├── cv/
│   ├── core/
│   │   ├── model_loader.py          ← Chargement YOLO (COCO + Custom)
│   │   └── depth_loader.py          ← Chargement Depth Anything V2
│   ├── detector.py                  ← Détection d'obstacles
│   ├── finder.py                    ← Recherche d'objet
│   └── localizer.py                 ← Identification de pièce
│
├── nlp/
│   ├── model_loader.py              ← Chargement SentenceTransformer + spaCy
│   ├── intent.py                    ← Détection d'intention + extraction d'entité
│   └── intents.json                 ← Exemples d'intentions vocales
│
├── navigation/
│   ├── graph.py                     ← Chargement du graphe maison
│   ├── pathfinder.py                ← Algorithme BFS
│   ├── instructions.py              ← Génération des instructions vocales
│   ├── house_default.json           ← Configuration maison par défaut
│   └── houses/                      ← Configs personnalisées par utilisateur
│
├── safety/
│   ├── __init__.py
│   └── sos.py                       ← Module alerte d'urgence
│
├── test/                            ← Scripts de test
│   ├── test_intent.py
│   ├── test_detector.py
│   ├── test_finder.py
│   ├── test_localizer.py
│   └── test_navigate.py
│
└── image_test/                      ← Images pour les tests CV
```

---

## Modèles à télécharger

### YOLO (automatique au premier lancement)

```
cv/models/
├── yolov8n.pt      ← téléchargé automatiquement par Ultralytics
└── best.pt         ← modèle custom (à placer manuellement)
```

> **best.pt** est le modèle custom entraîné pour détecter : `fire`, `hunman-fire`, `knife`, `stairs`.
> À télécharger depuis le drive du projet et placer dans `cv/models/`.

### Depth Anything V2 (automatique au premier lancement)

Téléchargé automatiquement depuis HuggingFace au premier démarrage (~100 MB).

### Modèles NLP (automatique au premier lancement)

- `paraphrase-multilingual-MiniLM-L12-v2` (~50 MB) — téléchargé dans `nlp/.model_cache/`
- `fr_core_news_sm` — installé via `python -m spacy download fr_core_news_sm`

---

## Lancement

### API principale (Flutter / tests Swagger)

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Swagger UI disponible sur : `http://127.0.0.1:8000/docs`

---

### Démo pipeline complet

```bash
cd backend
uvicorn demo:app --reload --port 8001
```

Swagger UI disponible sur : `http://127.0.0.1:8001/docs`

Route unique : `POST /pipeline` — envoie une phrase + une image, reçoit l'intention, le résultat CV et l'image annotée.

---

### Interface aidant (configuration maison)

```bash
cd backend
streamlit run caregiver.py
```

Interface disponible sur : `http://localhost:8501`

Permet à un aidant de configurer la maison d'un utilisateur malvoyant (pièces + connexions + directions).

---

## Routes API

| Route | Méthode | Description |
|-------|---------|-------------|
| `/` | GET | Vérification que le serveur tourne |
| `/detect-intent` | POST | Détection d'intention depuis une phrase |
| `/find-object` | POST | Recherche d'objet dans une image |
| `/where-am-i` | POST | Identification de la pièce courante |
| `/detect-obstacle` | POST | Détection d'obstacles en temps réel |
| `/navigate` | POST | Navigation guidée vers une pièce |
| `/sos` | POST | Déclenchement d'une alerte d'urgence |
| `/house/save` | POST | Sauvegarde config maison (1 fois par email) |
| `/house` | GET | Récupération config maison |
| `/house/update` | PUT | Mise à jour config maison existante |

---

## Tests

```bash
cd backend

# Test NLP
python test/test_intent.py

# Test détection d'obstacles
python test/test_detector.py

# Test recherche d'objet
python test/test_finder.py

# Test localisation
python test/test_localizer.py

# Test navigation
python test/test_navigate.py
```

---

## Variables d'environnement (optionnel)

```bash
# Désactiver le warning symlinks HuggingFace (Windows)
HF_HUB_DISABLE_SYMLINKS_WARNING=1

# Token HuggingFace pour éviter les rate limits
HF_TOKEN=hf_xxxxxxxxxxxx
```

Créer un fichier `.env` à la racine de `backend/` :

```
HF_HUB_DISABLE_SYMLINKS_WARNING=1
HF_TOKEN=hf_xxxxxxxxxxxx
```

---

## Premier démarrage

Le premier lancement est lent (~1-2 minutes) car plusieurs modèles sont téléchargés :

```
Chargement du modèle NLP (paraphrase-multilingual-MiniLM-L12-v2)...  ← ~10s
Modèle NLP chargé ✅
Chargement du modèle spaCy (fr_core_news_sm)...                       ← ~2s
Modèle spaCy chargé ✅
[ModelLoader] Chargement modèle COCO : cv/models/yolov8n.pt            ← ~5s
[ModelLoader] Modèle COCO prêt ✅
[ModelLoader] Chargement modèle custom : cv/models/best.pt             ← ~3s
[ModelLoader] Modèle custom prêt ✅
[DepthLoader] Chargement Depth Anything V2...                          ← ~10s
[DepthLoader] Modèle profondeur prêt ✅
[NLP] Encodage des classes YOLO...                                     ← ~2s
[NLP] Classes YOLO encodées ✅
```

Les lancements suivants sont beaucoup plus rapides (modèles en cache).

---

## Notes

- Les images annotées dans `static/` sont supprimées automatiquement après 30 secondes.
- Le dossier `temp/` contient les images temporaires pendant le traitement (supprimées immédiatement après).
- Ajouter `static/`, `temp/` et `nlp/.model_cache/` dans `.gitignore`.
