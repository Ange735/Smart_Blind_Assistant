# Installation

## 1. Cloner le dépôt

```bash
git clone https://github.com/votre-org/smart-blind-assistant.git
cd smart-blind-assistant
```

---

## 2. Backend FastAPI

### Créer un environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows
```

### Installer les dépendances

```bash
pip install -r requirements.txt
```

### Télécharger les modèles spaCy

```bash
python -m spacy download fr_core_news_sm
```

### Télécharger les modèles YOLO

Les modèles sont téléchargés automatiquement au premier lancement :

- `yolov8n.pt` — modèle COCO (80 classes) — téléchargé depuis Ultralytics
- `best.pt` — modèle custom dangers (4 classes) — à placer manuellement dans `cv/`
- `Depth Anything V2 Small` — téléchargé depuis HuggingFace au premier démarrage

!!! tip "Cache HuggingFace"
    Le modèle Depth Anything V2 (~100 Mo) est mis en cache dans `~/.cache/huggingface/` après le premier téléchargement. Les démarrages suivants sont instantanés.

### Structure des dossiers attendue

```
smart-blind-assistant/
├── main.py                    # Serveur FastAPI
├── cv/
│   ├── detector.py            # Surveillance d'obstacles
│   ├── finder.py              # Recherche et guidage d'objet
│   ├── localizer.py           # Identification de pièce
│   └── best.pt                # Modèle YOLO custom (dangers)
├── nlp/
│   └── intent.py              # Détection d'intention
├── navigation/
│   ├── navigator.py
│   └── houses/
│       └── house_default.json # Configuration de démonstration
├── safety/
│   └── sos.py
├── static/                    # Images annotées temporaires
├── caregiver.py               # Interface Streamlit aidant
└── requirements.txt
```

---

## 3. Application Flutter

```bash
cd flutter_app
flutter pub get
```

Configurer l'URL du backend dans `lib/config/api_config.dart` :

```dart
const String baseUrl = 'http://10.0.2.2:8000'; // Émulateur
// const String baseUrl = 'http://192.168.1.X:8000'; // Vrai téléphone
```

### Lancer l'application

```bash
flutter run
```

---

## 4. Interface Aidant (Streamlit)

```bash
streamlit run caregiver.py
```

L'interface s'ouvre sur `http://localhost:8501`.
