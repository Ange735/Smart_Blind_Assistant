# Modes de l'application

L'application Flutter a **4 modes** qui déterminent le comportement de la surveillance d'obstacles et l'interface visuelle.

---

## Tableau des modes

| Mode | Couleur | Icône | Comportement |
|------|---------|-------|-------------|
| `normal` | Blanc | `mic_none` | Surveillance active, prêt à écouter |
| `find_object` | Bleu | `stop` | Recherche en cours, rappel `/pipeline` toutes les 5s |
| `navigate` | Bleu | `stop` | Navigation en cours, rappel `/pipeline` toutes les 5s |
| `sos` | Rouge | `stop` | Urgence déclenchée, SosScreen affiché |

---

## Transitions entre modes

```
normal ──────────────────────────────────► find_object
  │         FIND_OBJECT intent + loop=true      │
  │                                             │ reached=true
  │◄────────────────────────────────────────────┘
  │
  ├──────────────────────────────────────► navigate
  │         NAVIGATE intent + loop=true         │
  │                                             │ destination atteinte
  │◄────────────────────────────────────────────┘
  │
  └──────────────────────────────────────► sos
            SOS intent + show_sos_screen=true    │
                                                 │ bouton annuler
            normal ◄─────────────────────────────┘
```

---

## Priorité des alertes par mode

| Mode actif | Alerte priorité 4 (feu) | Alerte priorité 1-3 | Guidage |
|------------|------------------------|---------------------|---------|
| `normal` | ✅ Interrompt tout | ✅ Si TTS libre | — |
| `find_object` | ✅ Interrompt tout | ❌ Ignorée | ✅ Prioritaire |
| `navigate` | ✅ Interrompt tout | ❌ Ignorée | ✅ Prioritaire |
| `sos` | — | — | — |
