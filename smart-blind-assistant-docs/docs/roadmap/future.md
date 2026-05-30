# Roadmap — Améliorations futures

## Vue d'ensemble

| Priorité | Amélioration | Effort estimé | Impact |
|----------|-------------|---------------|--------|
| 🔴 Haute | STT offline (Vosk/Whisper) | Moyen | Autonomie complète |
| 🔴 Haute | SOS réel via Twilio | Faible | Sécurité production |
| 🔴 Haute | Boussole Flutter intégrée | Faible | Navigation précise |
| 🟡 Moyenne | YOLO étendu (objets personnels) | Élevé | Couverture objets |
| 🟡 Moyenne | ARCore/ARKit profondeur | Élevé | Précision distance |
| 🟢 Faible | NLP amélioré (mpnet) | Faible | Meilleure sémantique |
| 🟢 Faible | Interface aidant dans Flutter | Moyen | UX aidant |
| 🟢 Faible | Route `/cancel` backend | Faible | Cohérence API |

---

## Détail des améliorations

### STT offline — Vosk / Whisper

Intégration d'un moteur de reconnaissance vocale **offline** pour permettre le fonctionnement sans connexion internet.

```python
# Option 1 : Vosk (léger, ~50 Mo par langue)
from vosk import Model, KaldiRecognizer

# Option 2 : Whisper (OpenAI, plus précis, ~150 Mo)
import whisper
model = whisper.load_model("small")
```

---

### SOS réel — Twilio

Remplacement de la simulation par de vrais appels téléphoniques :

```python
from twilio.rest import Client

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
call = client.calls.create(
    to="+212600000000",
    from_=TWILIO_PHONE,
    url="http://twiml-server/emergency"
)
```

---

### Boussole Flutter intégrée

```dart
FlutterCompass.events?.listen((event) {
  _currentHeading = event.heading;
});

// Inclure dans les appels /pipeline et /navigate :
body.fields['heading'] = _currentHeading.toString();
```

---

### YOLO étendu — Objets personnels

Créer un nouveau dataset sur Roboflow avec : clés, lunettes, portefeuille, télécommande, médicaments.

Entraîner un modèle `yolov8n_personal.pt` dédié aux objets personnels courants, à exécuter en parallèle des deux modèles existants.

---

### ARCore / ARKit — Profondeur centimétrique

Remplacer Depth Anything V2 par la profondeur native du smartphone pour une précision de l'ordre du centimètre sur les appareils compatibles.

---

### Modèle NLP amélioré

Remplacer `paraphrase-multilingual-MiniLM-L12-v2` par `paraphrase-multilingual-mpnet-base-v2` pour une meilleure précision sémantique (au coût d'une légère augmentation de la latence et de la mémoire).
