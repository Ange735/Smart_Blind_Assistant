# Codes de réponse et gestion d'erreurs

## Codes HTTP

| Code | Signification | Cas d'usage |
|------|---------------|-------------|
| `200 OK` | Succès | Traitement réussi |
| `400 Bad Request` | Requête invalide | Paramètres manquants ou malformés |
| `404 Not Found` | Ressource introuvable | Configuration maison non trouvée |
| `409 Conflict` | Conflit | Email déjà enregistré (`/house/save`) |
| `500 Internal Server Error` | Erreur serveur | Exception non gérée dans un module IA |

---

## Structure d'erreur

```json
{
  "status": "error",
  "message": "Description de l'erreur",
  "detail": "Stack trace ou contexte supplémentaire (optionnel)"
}
```

---

## Comportement de fallback

| Situation | Comportement backend |
|-----------|---------------------|
| Modèle IA lève une exception | Retourne JSON structuré avec `status='error'` |
| Pièce actuelle inconnue dans `/navigate` | Réponse claire avec TTS approprié |
| Maison non configurée | Charge automatiquement `house_default.json` |
| Image corrompue | Retourne erreur 400 avec message explicatif |

---

## Timeouts Flutter

L'application Flutter applique un **timeout de 15 secondes** sur tous les appels HTTP.

| Erreur | Message TTS affiché |
|--------|---------------------|
| Timeout dépassé | « Délai dépassé, réessayez. » |
| Erreur de connexion réseau | « Erreur de connexion au serveur. » |
| Caméra non disponible | Message vocal au démarrage + dégradation gracieuse |
| STT non disponible | « Microphone non disponible » + bouton désactivé |
