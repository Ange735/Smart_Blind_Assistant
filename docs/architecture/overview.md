# Vue d'ensemble de l'architecture

## Trois couches interdépendantes

La solution est structurée en **trois couches distinctes** qui communiquent via une API REST. Cette séparation stricte des responsabilités garantit la maintenabilité, l'évolutivité et la clarté du code.

```
┌─────────────────────────────────────────────────────────┐
│                    COUCHE PRÉSENTATION                  │
│                                                         │
│   App Flutter (Android)        Streamlit (caregiver.py) │
│   Interface vocale utilisateur  Interface aidant        │
└───────────────────────┬─────────────────────────────────┘
                        │  API REST (HTTP/JSON + multipart)
┌───────────────────────▼─────────────────────────────────┐
│                    COUCHE TRAITEMENT                     │
│                                                         │
│              Backend FastAPI (main.py)                  │
│         Orchestration — routage vers les modules IA     │
└────┬──────────────┬──────────────┬──────────────┬───────┘
     │              │              │              │
┌────▼────┐  ┌──────▼──────┐ ┌────▼────┐  ┌─────▼─────┐
│   CV    │  │     NLP     │ │  NAV    │  │  SAFETY   │
│  cv/    │  │   nlp/      │ │  nav/   │  │  safety/  │
└─────────┘  └─────────────┘ └─────────┘  └───────────┘
                    COUCHE INTELLIGENCE
```

---

## Rôle de chaque couche

| Couche | Composant | Rôle |
|--------|-----------|------|
| Présentation | App Flutter (Android) | Interface vocale utilisateur — STT, TTS, caméra |
| Présentation | Streamlit (caregiver.py) | Interface aidant — configuration de la maison |
| Traitement | Backend FastAPI (main.py) | Orchestration — routage vers les modules IA |
| Intelligence | Computer Vision (cv/) | Détection, recherche, localisation par image |
| Intelligence | NLP (nlp/) | Compréhension et analyse des commandes vocales |
| Intelligence | Navigation (navigation/) | Calcul de chemins et instructions de guidage |
| Urgence | Safety (safety/) | Gestion des alertes SOS |
| Données | navigation/houses/ | Configurations de maisons par utilisateur |

---

## Principe architectural fondamental

!!! abstract "Intelligence côté serveur uniquement"
    **Toute l'intelligence réside dans le backend.** L'application Flutter est un **client passif** qui exécute les instructions reçues sans les interpréter.

- Flutter ne contient **aucune logique métier** — il envoie des données, reçoit des instructions, les exécute.
- Le backend **décide de tout** : quel module appeler, quand boucler, quand vibrer, quand afficher l'urgence.
- Les mises à jour du système **ne nécessitent pas de mise à jour de l'application mobile**.

### Exemple concret

Quand l'utilisateur dit *« je cherche ma télécommande »* :

1. Flutter envoie la phrase + une frame caméra au backend (`POST /pipeline`)
2. Le backend retourne :
   ```json
   {
     "tts_message": "Tournez à droite",
     "action": {
       "loop": true,
       "loop_interval": 5
     }
   }
   ```
3. Flutter lit le message TTS et programme un rappel toutes les 5 secondes — **sans savoir pourquoi**.
