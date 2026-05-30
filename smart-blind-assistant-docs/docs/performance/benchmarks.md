# Benchmarks

## Latences par route

Ces mesures sont indicatives et dépendent du matériel. Mesurées sur CPU Intel Core i7 (pas de GPU) sauf mention contraire.

| Route | Opérations | Latence CPU | Latence GPU |
|-------|-----------|-------------|-------------|
| `POST /detect-obstacle` | YOLO×2 + Depth + NMS | ~400ms | ~80ms |
| `POST /find-object` | YOLO×2 + Depth + zones | ~350ms | ~70ms |
| `POST /where-am-i` | YOLO COCO + signatures | ~200ms | ~50ms |
| `POST /detect-intent` | SentenceTransformer + spaCy | ~50ms | ~50ms |
| `POST /pipeline` | NLP + module CV | ~450ms | ~130ms |
| `POST /navigate` | Localizer + BFS | ~220ms | ~60ms |

!!! note "Latence réseau"
    Sur réseau local WiFi, la latence réseau s'ajoute : ~5–20ms. Sur 4G/LTE : ~50–150ms supplémentaires.

---

## Cycle complet utilisateur

```
Utilisateur parle (2–5s)
  + STT transcription (~500ms)
  + HTTP POST /pipeline (~450ms CPU / ~130ms GPU)
  + TTS lecture (~1–3s)
────────────────────────────
Total ressenti : ~4–9 secondes
```

---

## Mémoire RAM totale (backend au repos)

| Composant | RAM |
|-----------|-----|
| Processus Python + FastAPI | ~80 Mo |
| Modèles IA chargés | ~190 Mo |
| **Total** | **~270 Mo** |

Compatible avec les serveurs entry-level (4 Go RAM).
