# Architecture Flutter

## Philosophie

!!! abstract "Client vocal passif"
    L'application Flutter est un **client vocal passif**. Elle ne contient aucune logique métier — elle se contente d'exécuter les instructions reçues du backend. Cette philosophie garantit une application **légère, stable et facile à maintenir**.

---

## Structure des fichiers

```
lib/
├── main.dart                  # Initialisation — caméra + lancement HomeScreen
├── config/
│   └── api_config.dart        # URL backend
├── services/
│   └── api_service.dart       # Couche réseau — pipeline(), detectObstacle(), cancel()
└── screens/
    ├── home_screen.dart        # Écran principal — orchestration caméra, STT, TTS, timers
    └── sos_screen.dart         # Écran urgence — fond rouge, message vocal, bouton annuler
```

---

## Couche réseau — `api_service.dart`

```dart
class ApiService {
  static const Duration timeout = Duration(seconds: 15);

  Future<Map<String, dynamic>> pipeline(String phrase, Uint8List imageBytes, String deviceId);
  Future<Map<String, dynamic>> detectObstacle(Uint8List imageBytes);
  Future<void> cancel();
}
```

Les images sont envoyées en **bytes directement depuis la mémoire** (`Uint8List`) via `MultipartFile.fromBytes()`, évitant les écritures sur le disque du téléphone.

---

## Surveillance d'obstacles — Boucle permanente

```dart
Timer.periodic(Duration(seconds: 5), (timer) async {
  final frame = await _captureFrame();
  final response = await ApiService.detectObstacle(frame);

  if (response['interrupt'] == true || response['priorite'] >= 4) {
    _tts.stop();  // Interrompre TTS en cours
    _tts.speak(response['alerts'][0]['tts_message']);
  } else if (_currentMode == AppMode.normal && !_tts.isSpeaking) {
    _tts.speak(response['alerts'][0]['tts_message']);
  }
  // En mode find_object ou navigate : alertes normales ignorées
});
```

---

## Flux STT — Commande vocale

```
Appui bouton micro
  │
  ├── Vérification STT disponible
  ├── Arrêt TTS en cours + délai 100ms
  ├── TTS: "Je vous écoute"
  ├── Écoute (pauseFor=3s, timeout=12s)
  ├── Détection mots d'annulation
  └── POST /pipeline (phrase + frame)
```

---

## Annulation

L'utilisateur peut annuler toute action en cours de deux façons :

- **Appui long** sur le bouton micro → `_cancelCurrentAction()` direct
- **Commande vocale** : `stop`, `annuler`, `arrête`, `stopper`, `quitter`, `terminer`
