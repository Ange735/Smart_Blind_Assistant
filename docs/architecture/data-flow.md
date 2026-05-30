# Flux de données

## Flux principal — Commande vocale

```
Utilisateur parle
      │
      ▼
[Flutter] Capture audio STT
      │  Phrase transcrite
      ▼
[Flutter] Capture frame caméra
      │
      ▼
[Flutter] POST /pipeline
         { phrase, image (bytes) }
      │
      ▼
[Backend] NLP — détection intention
      │
      ├── FIND_OBJECT → cv/finder.py
      ├── NAVIGATE    → navigation/navigator.py
      ├── LOCATE_ROOM → cv/localizer.py
      ├── SOS         → safety/sos.py
      └── UNKNOWN     → réponse "Je n'ai pas compris"
      │
      ▼
[Backend] Construction réponse JSON
      │  { tts_message, action, image_url }
      ▼
[Flutter] Lecture TTS du message
[Flutter] Exécution de l'action
         (loop timer, vibration, SOS screen...)
```

---

## Flux surveillance d'obstacles (boucle permanente)

```
Timer.periodic(5 secondes)
      │
      ▼
[Flutter] Capture frame caméra
      │
      ▼
[Flutter] POST /detect-obstacle
      │
      ▼
[Backend] cv/detector.py
         → YOLO COCO + YOLO Custom (parallèle)
         → NMS inter-modèles (IoU > 0.5)
         → Depth Anything V2 (distance)
         → Tri par priorité (0–4)
      │
      ▼
[Backend] Réponse JSON
         { alerts: [...], priorite: N, interrupt: bool }
      │
      ▼
[Flutter] Priorité 4 (feu) → interrupt TTS + alerte immédiate
[Flutter] Priorité 1–3    → alerte si TTS libre
[Flutter] Mode find/nav   → alertes normales ignorées
```

---

## Flux SOS

```
Phrase d'urgence détectée (NLP → SOS)
      │
      ▼
[Backend] safety/sos.py
         → Log horodaté (timestamp ISO, user ID, phrase, GPS)
         → Simulation appel 15/18/112
         → Notification contacts (simulation)
      │
      ▼
[Backend] Réponse JSON
         { tts_message, action: { vibrate: true, show_sos_screen: true } }
      │
      ▼
[Flutter] Vibration forte 1000ms
[Flutter] Navigation vers SosScreen (fond rouge)
[Flutter] TTS: "SOS déclenché, les secours ont été alertés, restez en ligne."
```

---

## Flux configuration maison (aidant)

```
[Streamlit caregiver.py]
      │
      ├── Saisie email + pièces + connexions
      │
      ├── POST /house/save
      │      → Vérification unicité email
      │      → Sauvegarde JSON : house_{email_sanitized}.json
      │
      └── PUT /house/update (modification ultérieure)
```
