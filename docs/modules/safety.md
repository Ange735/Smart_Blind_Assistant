# Module Safety — Alertes SOS

## Déclenchement

Le module SOS se déclenche dès qu'une **phrase d'urgence** est détectée par le NLP :

```
"au secours"   "j'ai besoin d'aide"   "appelle le 15"
"je suis tombé"   "urgence"   "help"   "je me sens mal"
```

---

## Actions du module

Quand un SOS est déclenché, `safety/sos.py` effectue les actions suivantes :

### 1. Log horodaté complet

```json
{
  "timestamp": "2026-05-30T14:32:17.843Z",
  "user_id": "utilisateur@example.com",
  "phrase": "au secours, je suis tombé",
  "gps": {"lat": 33.5731, "lon": -7.5898}
}
```

### 2. Simulation d'appel d'urgence

```
[console] Appel vers 15/18/112 en cours...
```

En production, remplaçable par un vrai appel via **Twilio**.

### 3. Notification contacts

Simulation de notification aux proches (SMS/appel). Remplaçable par une vraie intégration en production.

---

## Réponse vers Flutter

```json
{
  "tts_message": "SOS déclenché, les secours ont été alertés, restez en ligne.",
  "action": {
    "vibrate": true,
    "vibrate_duration": 1000,
    "show_sos_screen": true,
    "loop": false
  }
}
```

## Comportement Flutter

Suite à la réponse SOS :

1. **Vibration forte** — 1000ms
2. **Navigation vers `SosScreen`** — fond rouge, icône urgence
3. **Message vocal TTS** — « SOS déclenché, les secours ont été alertés, restez en ligne. »
4. **Bouton Annuler** disponible pour revenir au mode normal

---

!!! warning "SOS en production"
    Le SOS actuel est une **simulation** (log + console). Pour une mise en production, intégrer Twilio pour les appels téléphoniques réels et un service de notification push pour les contacts d'urgence.
