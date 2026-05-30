# Le Pipeline en détail

## Principe

Le pipeline (`POST /pipeline`) est la route unifiée qui orchestre l'ensemble du traitement. Flutter n'a besoin que de cette route pour les commandes vocales.

---

## Intentions supportées

| Intention | Déclenchée par | Module appelé |
|-----------|---------------|---------------|
| `FIND_OBJECT` | « cherche », « retrouve », « où est » | `cv/finder.py` |
| `NAVIGATE` | « emmène-moi », « aller à », « guide-moi » | `navigation/navigator.py` |
| `LOCATE_ROOM` | « où suis-je », « quelle pièce », « je suis où » | `cv/localizer.py` |
| `SOS` | « au secours », « urgence », « j'ai besoin d'aide » | `safety/sos.py` |
| `UNKNOWN` | Tout le reste | Réponse « Je n'ai pas compris » |

---

## Structure de la réponse complète

```json
{
  "tts_message": "string",
  "action": {
    "loop": false,
    "loop_interval": 5,
    "vibrate": false,
    "vibrate_duration": 0,
    "stop_obstacle_detection": false,
    "show_sos_screen": false
  },
  "image_url": "string | null",
  "intent": "FIND_OBJECT | NAVIGATE | LOCATE_ROOM | SOS | UNKNOWN",
  "entity": "string | null",
  "reached": false,
  "source": "sentence_transformer | spacy_verbe | fallback_entite | unknown"
}
```

## Champ `action` — Référence

| Champ | Type | Description |
|-------|------|-------------|
| `loop` | bool | Flutter doit rappeler /pipeline toutes les `loop_interval` secondes |
| `loop_interval` | int | Intervalle en secondes (défaut : 5) |
| `vibrate` | bool | Déclencher une vibration haptique |
| `vibrate_duration` | int | Durée de vibration en millisecondes |
| `stop_obstacle_detection` | bool | Stopper la boucle de surveillance d'obstacles |
| `show_sos_screen` | bool | Afficher l'écran d'urgence SOS |
