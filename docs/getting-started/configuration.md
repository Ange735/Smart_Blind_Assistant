# Configuration

## Lancer le backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Au démarrage, tous les modèles IA sont chargés en mémoire (pattern Singleton). Cette opération prend **10–15 secondes** la première fois.

| Modèle | Temps de chargement | Mémoire |
|--------|---------------------|---------|
| SentenceTransformer MiniLM | ~3s (cache local) | ~50 Mo |
| spaCy fr_core_news_sm | ~1s | ~15 Mo |
| YOLOv8n COCO | ~2s | ~12 Mo |
| YOLOv8n Custom (best.pt) | ~2s | ~12 Mo |
| Depth Anything V2 Small | ~5s (cache HuggingFace) | ~100 Mo |
| Embeddings YOLO (84 classes) | ~2s | négligeable |

### Vérifier que le serveur est opérationnel

```bash
curl http://localhost:8000/
```

Réponse attendue :

```json
{"status": "ok", "message": "Smart Blind Assistant API is running"}
```

La documentation Swagger interactive est disponible sur :

```
http://localhost:8000/docs
```

---

## Configuration de la maison (Interface Aidant)

La configuration de la maison est effectuée **une seule fois** par un aidant via l'interface Streamlit.

1. Lancer `streamlit run caregiver.py`
2. Saisir l'email de l'utilisateur malvoyant
3. Ajouter les pièces une par une
4. Définir les connexions entre pièces (source → destination + direction cardinale)
5. Cliquer sur **Sauvegarder**

!!! info "Règle d'unicité"
    Un email ne peut être enregistré qu'une seule fois via `POST /house/save`. Pour modifier une configuration existante, utiliser le bouton **Modifier** qui appelle `PUT /house/update`.

### Format JSON de la configuration maison

```json
{
  "email": "utilisateur@example.com",
  "rooms": ["salon", "cuisine", "chambre", "salle_de_bain", "bureau"],
  "connections": [
    {"from": "salon", "to": "cuisine", "angle": 90},
    {"from": "salon", "to": "chambre", "angle": 0},
    {"from": "chambre", "to": "salle_de_bain", "angle": 90},
    {"from": "salon", "to": "bureau", "angle": 270}
  ]
}
```

!!! tip "Angles absolus"
    Les angles sont en degrés absolus : 0° = Nord, 90° = Est, 180° = Sud, 270° = Ouest. Le système calcule dynamiquement gauche/droite/avancez selon l'orientation réelle de l'utilisateur (boussole du smartphone).

### Conversion email → fichier

L'email `utilisateur@example.com` est converti en `house_utilisateur_example_com.json` via :

```python
import re
filename = "house_" + re.sub(r'[^\w]', '_', email.lower()) + ".json"
```

Cette conversion est identique dans Streamlit et dans le backend, garantissant que les deux pointent vers le même fichier.
