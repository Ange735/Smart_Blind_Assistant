# 📱 Smart Blind Assistant — Guide complet

Assistant intelligent pour malvoyants — Backend FastAPI + Computer Vision + NLP + Application Flutter

---

## Prérequis

- Python 3.10+
- Flutter SDK
- Android Studio (pour ADB)
- Un téléphone Android avec **Mode développeur** activé
- Les deux appareils connectés au **même réseau WiFi**

---

## Structure du projet

```
Smart_Blind_Assistant/
├── backend/                          ← Serveur FastAPI (Python)
│   ├── main.py                       ← API REST principale
│   ├── demo.py                       ← Pipeline de démonstration (port 8001)
│   ├── caregiver.py                  ← Interface Streamlit aidant
│   ├── cv/
│   │   ├── core/
│   │   │   ├── model_loader.py       ← Chargement YOLO (COCO + Custom)
│   │   │   └── depth_loader.py       ← Chargement Depth Anything V2
│   │   ├── detector.py               ← Détection d'obstacles
│   │   ├── finder.py                 ← Recherche d'objet
│   │   └── localizer.py              ← Identification de pièce
│   ├── nlp/
│   │   ├── model_loader.py           ← Chargement SentenceTransformer + spaCy
│   │   ├── intent.py                 ← Détection d'intention + extraction d'entité
│   │   └── intents.json              ← Exemples d'intentions vocales
│   ├── navigation/
│   │   ├── graph.py                  ← Chargement du graphe maison
│   │   ├── pathfinder.py             ← Algorithme BFS
│   │   ├── instructions.py           ← Génération des instructions vocales
│   │   ├── house_default.json        ← Configuration maison par défaut
│   │   └── houses/                   ← Configs personnalisées par utilisateur
│   ├── safety/
│   │   └── sos.py                    ← Module alerte d'urgence
│   └── test/                         ← Scripts de test
│
└── smart_blind_app/                  ← Application Flutter
    └── lib/
        ├── main.dart
        ├── config/
        │   └── api_config.dart       ← ⚠️ URL du backend à configurer
        ├── screens/
        │   ├── home_screen.dart      ← Écran principal
        │   └── sos_screen.dart       ← Écran SOS
        └── services/
            └── api_service.dart      ← Appels API
```

---

## 1. Installer et lancer le backend

### Cloner le projet

```bash
git clone <repo>
cd Smart_Blind_Assistant/backend
```

### Créer et activer l'environnement virtuel

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac / Linux
python -m venv .venv
source .venv/bin/activate
```

### Installer les dépendances

```bash
pip install -r requirements.txt
```

Si `requirements.txt` n'existe pas :

```bash
pip install fastapi uvicorn python-multipart
pip install ultralytics
pip install transformers torch pillow
pip install sentence-transformers scikit-learn
pip install spacy && python -m spacy download fr_core_news_sm
pip install streamlit requests opencv-python numpy
```

### Modèles à télécharger

| Modèle | Taille | Téléchargement |
|--------|--------|----------------|
| `yolov8n.pt` | ~6 MB | Automatique (Ultralytics) |
| `best.pt` | — | Manuel → placer dans `cv/models/` |
| Depth Anything V2 | ~100 MB | Automatique (HuggingFace) |
| `paraphrase-multilingual-MiniLM-L12-v2` | ~50 MB | Automatique (HuggingFace) |
| `fr_core_news_sm` | ~15 MB | `python -m spacy download fr_core_news_sm` |

> **best.pt** est le modèle custom pour détecter : `fire`, `knife`, `stairs`, `hunman-fire`. À récupérer depuis le drive du projet.

### Lancer l'API

```bash
# Pour le téléphone (obligatoire)
uvicorn main:app --host 0.0.0.0 --port 8000

# Pour tester en local seulement
uvicorn main:app --reload --port 8000
```

> ⚠️ Le `--host 0.0.0.0` est obligatoire pour que le téléphone puisse accéder au backend.

Swagger UI disponible sur : `http://127.0.0.1:8000/docs`

### Premier démarrage (1-2 minutes)

```
Chargement du modèle NLP...   ✅
Modèle spaCy chargé...        ✅
Modèle COCO prêt...           ✅
Modèle custom prêt...         ✅
Depth Anything V2 prêt...     ✅
Classes YOLO encodées...      ✅
```

Les lancements suivants sont beaucoup plus rapides (modèles en cache).

---

## 2. Configurer et lancer l'application Flutter

### Trouver l'IP de ton PC

```bash
# Windows
ipconfig
# → cherche "IPv4 Address" sous "Wireless LAN adapter Wi-Fi"

# Mac/Linux
ifconfig | grep inet
```

### Configurer l'URL du backend

Modifier `smart_blind_app/lib/config/api_config.dart` :

```dart
import 'package:flutter/foundation.dart';

class ApiConfig {
  static String get baseUrl {
    if (kIsWeb) {
      return "http://127.0.0.1:8000";       // Chrome
    } else {
      return "http://192.168.X.X:8000";     // ← Remplace par l'IP de ton PC
    }
  }
}
```

### Connecter le téléphone Android en WiFi (ADB)

**Ajouter ADB au PATH (Windows) :**

```cmd
set PATH=%PATH%;C:\Users\<ton-user>\AppData\Local\Android\Sdk\platform-tools
```

**Activer le débogage sans fil sur le téléphone :**

1. Paramètres → À propos → tape **7 fois** sur "Numéro de build"
2. Paramètres → Options développeur → active **Débogage sans fil**
3. Clique **"Pair device with pairing code"** → note l'IP:port et le code à 6 chiffres

**Appairer et connecter :**

```cmd
# Appairage (une seule fois par session)
adb pair 192.168.X.X:XXXXX
# → entre le code à 6 chiffres

# Connexion
adb connect 192.168.X.X:YYYYY
# ⚠️ Utilise le port affiché sur l'écran "Débogage sans fil", pas forcément 5555

# Vérifier
adb devices
```

### Lancer l'application

```bash
cd smart_blind_app

# Voir les appareils connectés
flutter devices

# Lancer sur le téléphone
flutter run -d <device-id>
# Exemple : flutter run -d 192.168.11.159:45411
```

---

## 3. Utilisation de l'app

| Action | Description |
|--------|-------------|
| **Appui court** sur le micro | Active l'écoute vocale |
| **Appui long** sur le micro | Annule l'action en cours |
| Dire "stop" / "annuler" / "arrête" | Annule l'action en cours vocalement |

### Modes

| Indicateur | Mode | Description |
|------------|------|-------------|
| 🟢 Vert | Surveillance active | Détection d'obstacles automatique toutes les 5s |
| 🟠 Orange | Recherche d'objet | Recherche un objet en boucle |
| 🔵 Bleu | Navigation | Guide vocal en cours |
| 🔴 Rouge | SOS | Alerte d'urgence déclenchée |

---

## 4. Routes API

| Route | Méthode | Description |
|-------|---------|-------------|
| `/` | GET | Vérification serveur |
| `/detect-obstacle` | POST | Détection d'obstacles en temps réel |
| `/pipeline` | POST | Pipeline principal (phrase + image) |
| `/detect-intent` | POST | Détection d'intention depuis une phrase |
| `/find-object` | POST | Recherche d'objet dans une image |
| `/where-am-i` | POST | Identification de la pièce courante |
| `/navigate` | POST | Navigation guidée vers une pièce |
| `/sos` | POST | Alerte d'urgence |
| `/house/save` | POST | Sauvegarde config maison |
| `/house` | GET | Récupération config maison |
| `/house/update` | PUT | Mise à jour config maison |

---

## 5. Outils supplémentaires

### Pipeline de démonstration

```bash
uvicorn demo:app --reload --port 8001
# → http://127.0.0.1:8001/docs
```

### Interface aidant (configuration maison)

```bash
streamlit run caregiver.py
# → http://localhost:8501
```

### Tests backend

```bash
python test/test_intent.py
python test/test_detector.py
python test/test_finder.py
python test/test_localizer.py
python test/test_navigate.py
```

---

## 6. Reconnexion rapide (sessions suivantes)

```cmd
# Sur le téléphone : Options développeur → Débogage sans fil → Pair device with pairing code
adb pair 192.168.X.X:XXXXX
adb connect 192.168.X.X:YYYYY
flutter run -d <device-id>
```

---

## Problèmes fréquents

| Problème | Solution |
|----------|----------|
| `adb` non reconnu | Ajouter `platform-tools` au PATH |
| `cannot connect to X:5555` | Utiliser le port affiché sur le téléphone, pas 5555 |
| Double connexion ADB | `adb disconnect` puis reconnecter |
| "Erreur de connexion au serveur" | Vérifier `--host 0.0.0.0` et l'IP dans `api_config.dart` |
| NDK corrompu | Supprimer `AppData\Local\Android\sdk\ndk\<version>` et relancer |
| STT ne répond pas | Vérifier les permissions microphone sur le téléphone |
| App crash au démarrage caméra | Vérifier les permissions caméra dans les paramètres Android |

---

## Variables d'environnement (optionnel)

Créer un fichier `.env` dans `backend/` :

```
HF_HUB_DISABLE_SYMLINKS_WARNING=1
HF_TOKEN=hf_xxxxxxxxxxxx
```
