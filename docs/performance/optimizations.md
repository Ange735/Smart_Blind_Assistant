# Performance et optimisations

## Chargement des modèles — Pattern Singleton

Tous les modèles IA sont chargés **une seule fois au démarrage** et maintenus en mémoire via le pattern Singleton Thread-Safe.

```python
import threading

class ModelSingleton:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double vérification
                    cls._instance = cls._load_models()
        return cls._instance
```

Un `threading.Lock()` avec double vérification évite les chargements parallèles si plusieurs requêtes arrivent simultanément au démarrage.

---

## Temps de chargement et mémoire

| Modèle | Temps de chargement | Mémoire approximative |
|--------|---------------------|-----------------------|
| SentenceTransformer MiniLM | ~3s (cache local) | ~50 Mo |
| spaCy fr_core_news_sm | ~1s | ~15 Mo |
| YOLOv8n COCO | ~2s | ~12 Mo |
| YOLOv8n Custom (best.pt) | ~2s | ~12 Mo |
| Depth Anything V2 Small | ~5s (cache HuggingFace) | ~100 Mo |
| Embeddings YOLO (84 classes) | ~2s (au démarrage) | négligeable |
| **Total** | **~15s** | **~190 Mo** |

---

## Exécution parallèle des modèles YOLO

Les deux modèles YOLO sont exécutés **simultanément** via `ThreadPoolExecutor` :

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=2) as executor:
    future_coco = executor.submit(yolo_coco.predict, image)
    future_custom = executor.submit(yolo_custom.predict, image)
    results_coco = future_coco.result()
    results_custom = future_custom.result()
```

| Mode | Temps d'inférence |
|------|------------------|
| GPU RTX 3050 (parallèle) | ~50–80ms |
| GPU RTX 3050 (séquentiel) | ~200ms |
| CPU (parallèle) | ~200–400ms |
| **Gain GPU** | **~60%** |

---

## Gestion des fichiers temporaires

| Fichier | Suppression |
|---------|------------|
| Image d'entrée | Immédiatement après traitement |
| Image annotée (static/) | Après 30 secondes (BackgroundTask) |

Les noms de fichiers sont des **UUIDs** (`uuid4()`) — aucun conflit entre requêtes concurrentes.

---

## Envoi d'images par bytes

Flutter envoie les frames en bytes **directement depuis la mémoire** (`Uint8List`) via `MultipartFile.fromBytes()`, évitant les écritures sur le disque du téléphone.

```dart
final request = http.MultipartRequest('POST', uri);
request.files.add(
  http.MultipartFile.fromBytes('image', imageBytes, filename: 'frame.jpg')
);
```

**Avantages** :
- Réduit la latence (pas d'I/O disque)
- Réduit la consommation batterie
- Évite les problèmes de permissions stockage
