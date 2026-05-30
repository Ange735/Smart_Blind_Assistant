# Dépendances Flutter

## `pubspec.yaml` — packages principaux

```yaml
dependencies:
  flutter:
    sdk: flutter

  camera: ^0.11.0
  speech_to_text: ^7.0.0
  flutter_tts: ^4.0.0
  http: ^1.2.0
  vibration: ^2.0.0
  permission_handler: ^11.0.0
  flutter_compass: ^0.8.0
```

---

## Détail des packages

| Package | Version | Rôle |
|---------|---------|------|
| `camera` | ^0.11.0 | Capture de frames en temps réel — bytes directs en mémoire |
| `speech_to_text` | ^7.0.0 | STT natif — reconnaissance vocale offline/online |
| `flutter_tts` | ^4.0.0 | TTS natif — voix française automatiquement sélectionnée |
| `http` | ^1.2.0 | Requêtes HTTP multipart — bytes + champs texte |
| `vibration` | ^2.0.0 | Vibration haptique 1000ms pour SOS |
| `permission_handler` | ^11.0.0 | Caméra, microphone, internet |
| `flutter_compass` | ^0.8.0 | Boussole pour heading navigation |

---

## Permissions Android (`AndroidManifest.xml`)

```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.VIBRATE" />
```

---

!!! warning "STT et connectivité"
    Le package `speech_to_text` utilise l'API de reconnaissance vocale Google par défaut, qui nécessite une **connexion internet**. Une intégration offline (Vosk, Whisper) est prévue dans les améliorations futures.
