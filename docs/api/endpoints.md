# Référence API REST

## Base URL

```
http://<host>:8000
```

---

## Endpoints

### `GET /`

Vérification que le serveur est opérationnel.

**Réponse**
```json
{"status": "ok", "message": "Smart Blind Assistant API is running"}
```

---

### `POST /pipeline`

**Route principale** : phrase + image → NLP + CV + instructions Flutter.

**Corps de la requête** (`multipart/form-data`)

| Champ | Type | Description |
|-------|------|-------------|
| `phrase` | string | Commande vocale transcrite |
| `image` | file | Frame caméra (JPEG/PNG) |
| `device_id` | string | Email ou identifiant utilisateur |

**Réponse**
```json
{
  "tts_message": "Tournez à droite",
  "action": {
    "loop": true,
    "loop_interval": 5,
    "vibrate": false,
    "show_sos_screen": false,
    "stop_obstacle_detection": false
  },
  "image_url": "/static/uuid.jpg",
  "intent": "FIND_OBJECT",
  "entity": "remote",
  "reached": false,
  "source": "spacy_verbe"
}
```

---

### `POST /detect-intent`

NLP seul : analyse une phrase et retourne l'intention + entité.

**Corps** (`application/json`)
```json
{"phrase": "je cherche ma télécommande"}
```

**Réponse**
```json
{
  "intent": "FIND_OBJECT",
  "entity": "remote",
  "source": "sentence_transformer",
  "score": 0.84
}
```

---

### `POST /find-object`

Recherche un objet dans une image et génère des instructions de guidage.

**Corps** (`multipart/form-data`)

| Champ | Type | Description |
|-------|------|-------------|
| `object_class` | string | Classe YOLO de l'objet (ex: `remote`, `bed`) |
| `image` | file | Frame caméra |

**Réponse**
```json
{
  "tts_message": "Tournez légèrement à gauche, télécommande est presque là.",
  "reached": false,
  "direction": "slightly_left",
  "distance": "proche",
  "image_url": "/static/uuid.jpg"
}
```

---

### `POST /where-am-i`

Identifie la pièce courante depuis une image caméra.

**Corps** (`multipart/form-data`) : `image` (file)

**Réponse**
```json
{
  "room": "chambre",
  "confidence": 0.85,
  "tts_message": "Vous êtes dans la chambre.",
  "image_url": "/static/uuid.jpg"
}
```

---

### `POST /detect-obstacle`

Détecte les obstacles et génère les alertes vocales prioritaires.

**Corps** (`multipart/form-data`) : `image` (file)

**Réponse**
```json
{
  "alerts": [
    {
      "label": "chaise",
      "direction": "gauche",
      "distance": "proche",
      "priority": 1,
      "tts_message": "Obstacle détecté, chaise à votre gauche."
    }
  ],
  "priorite": 1,
  "interrupt": false,
  "image_url": "/static/uuid.jpg"
}
```

---

### `POST /navigate`

Navigation guidée : détecte pièce actuelle + génère chemin + instructions.

**Corps** (`multipart/form-data`)

| Champ | Type | Description |
|-------|------|-------------|
| `destination` | string | Pièce cible (ex: `cuisine`) |
| `image` | file | Frame caméra |
| `device_id` | string | Email utilisateur |
| `heading` | float (optionnel) | Orientation boussole en degrés |

---

### `POST /sos`

Déclenche une alerte d'urgence avec log et simulation d'appel.

**Corps** (`application/json`)
```json
{
  "device_id": "utilisateur@example.com",
  "phrase": "au secours",
  "gps": {"lat": 33.57, "lon": -7.58}
}
```

---

### `POST /house/save`

Sauvegarde la configuration maison d'un utilisateur (une fois par email).

**Corps** (`application/json`) : objet maison complet (voir [Configuration](../getting-started/configuration.md))

**Erreur si email déjà existant** :
```json
{"detail": "Configuration already exists for this email. Use PUT /house/update to modify."}
```

---

### `GET /house`

Récupère la configuration maison d'un utilisateur.

**Paramètre query** : `device_id=utilisateur@example.com`

---

### `PUT /house/update`

Met à jour une configuration maison existante.
