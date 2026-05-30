# Prérequis

Avant d'installer Smart Blind Assistant, assurez-vous que votre environnement répond aux exigences suivantes.

---

## Environnement serveur (Backend)

### Python

```
Python >= 3.9
```

### Matériel recommandé

| Composant | Minimum | Recommandé |
|-----------|---------|------------|
| CPU | 4 cœurs | 8 cœurs |
| RAM | 4 Go | 8 Go |
| GPU | — | NVIDIA RTX (CUDA) |
| Stockage | 5 Go libres | 10 Go libres |

!!! note "Sans GPU"
    Le système fonctionne entièrement sur CPU. L'inférence YOLO prend alors ~200ms en séquentiel contre ~50–80ms sur GPU.

### Dépendances Python principales

```
fastapi
uvicorn
ultralytics          # YOLOv8
transformers         # Depth Anything V2
sentence-transformers
spacy
torch
opencv-python
Pillow
numpy
streamlit            # Interface aidant
```

---

## Environnement mobile (Flutter)

| Outil | Version minimale |
|-------|-----------------|
| Flutter SDK | >= 3.0 |
| Dart | >= 3.0 |
| Android SDK | API 21 (Android 5.0) |
| Android Studio | Flamingo ou supérieur |

### Permissions requises sur Android

- `CAMERA` — capture de frames en temps réel
- `RECORD_AUDIO` — reconnaissance vocale STT
- `INTERNET` — communication avec le backend
- `VIBRATE` — alertes haptiques SOS

---

## Connectivité réseau

Le backend et l'application mobile doivent être sur le **même réseau local**, ou le backend doit être accessible via une URL publique.

!!! warning "Émulateur Android"
    Sur émulateur Android, l'adresse du backend est `10.0.2.2:8000` (redirection vers `localhost` de la machine hôte). Sur un vrai téléphone, utilisez l'IP locale de la machine hébergeant le backend.
