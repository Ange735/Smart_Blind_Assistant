# Backend FastAPI

## Pourquoi FastAPI ?

FastAPI est un framework Python moderne conçu pour les API hautes performances. Il a été retenu pour plusieurs raisons techniques :

| Critère | Avantage FastAPI |
|---------|-----------------|
| Performances | Comparable à Node.js et Go — bien supérieur à Flask/Django REST pour les opérations asynchrones |
| Fichiers multipart | Gestion native essentielle pour recevoir les images envoyées par Flutter |
| Documentation | Interface Swagger générée automatiquement sur `/docs` |
| Validation | Typage fort avec Pydantic — validation automatique des données entrantes |
| Tâches asynchrones | `BackgroundTasks` : suppression des fichiers temporaires sans bloquer la réponse |

---

## Le Pipeline — Route centrale

La route `/pipeline` est le **cœur du système**. Elle orchestre l'ensemble du traitement en une seule requête.

```
POST /pipeline
  │
  ├── 1. Prétraitement
  │      Sauvegarde de l'image (UUID), nettoyage de la phrase (lowercase + strip)
  │
  ├── 2. NLP / intent.py
  │      Détection de l'intention : FIND_OBJECT | NAVIGATE | LOCATE_ROOM | SOS | UNKNOWN
  │
  ├── 3. Extraction d'entité
  │      Extraction de l'objet ou du lieu mentionné dans la phrase
  │
  ├── 4. Routage
  │      Appel du module CV ou navigation selon l'intention détectée
  │
  ├── 5. Annotation
  │      Dessin des résultats sur l'image (bounding boxes, labels)
  │
  ├── 6. Construction de la réponse
  │      tts_message + action + image_url
  │
  └── 7. Nettoyage (BackgroundTask)
         Suppression des fichiers temporaires après 30 secondes
```

### Structure de la réponse

```json
{
  "tts_message": "Tournez légèrement à droite, télécommande est presque là.",
  "action": {
    "loop": true,
    "loop_interval": 5,
    "vibrate": false,
    "vibrate_duration": 0,
    "stop_obstacle_detection": false,
    "show_sos_screen": false
  },
  "image_url": "/static/abc123.jpg",
  "intent": "FIND_OBJECT",
  "entity": "remote",
  "reached": false
}
```

!!! info "Champ `action`"
    L'objet `action` dit à Flutter **exactement quoi faire** : boucler, vibrer, stopper la surveillance, afficher l'urgence. Flutter n'a aucune décision à prendre.

---

## Gestion des images annotées

En mode développement/test, chaque réponse des routes CV contient une `image_url` : l'image de la caméra avec les bounding boxes et labels dessinés.

- Les noms de fichiers sont des **UUIDs** — pas de conflits entre requêtes simultanées
- Les images d'entrée sont supprimées **immédiatement** après traitement
- Les images annotées sont supprimées après **30 secondes** via `BackgroundTasks`
- En production avec Flutter, ce champ peut être ignoré — il ne sert qu'au **debug visuel**
