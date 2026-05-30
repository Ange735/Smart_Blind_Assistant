# Premier lancement

## Scénario de démonstration

Ce guide illustre un parcours utilisateur complet avec la configuration de démonstration (`house_default.json`, 5 pièces).

---

### Étape 1 — Démarrer le backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Attendez le message de confirmation dans la console :
```
INFO:     Application startup complete.
```

---

### Étape 2 — Lancer l'application Flutter

```bash
flutter run
```

L'application démarre en **mode normal** (fond blanc, icône micro).

---

### Étape 3 — Tester la surveillance d'obstacles

Toutes les 5 secondes, l'application envoie automatiquement une frame à `/detect-obstacle`. Si un obstacle est détecté à proximité, une alerte vocale est prononcée :

```
"Obstacle détecté, chaise à votre gauche."
```

En cas de danger critique (feu, couteau, escaliers), l'alerte interrompt immédiatement toute autre action en cours.

---

### Étape 4 — Tester la recherche d'objet

Appuyer sur le bouton micro et dire :

```
"Je cherche ma télécommande"
```

Le backend retourne des instructions de guidage (ex. `"Tournez légèrement à droite"`). L'application entre en **mode find_object** (fond bleu) et envoie une frame toutes les 5 secondes jusqu'à ce que l'objet soit atteint (`reached=true`).

---

### Étape 5 — Tester la localisation

Appuyer sur le bouton micro et dire :

```
"Je suis où là ?"
```

Le système analyse les objets visibles et répond :

```
"Vous êtes dans le salon."
```

---

### Étape 6 — Tester la navigation

```
"Emmène-moi à la cuisine"
```

Le système détecte la pièce actuelle, calcule le chemin optimal (BFS), et guide l'utilisateur pas à pas.

---

### Étape 7 — Tester le SOS

```
"Au secours, j'ai besoin d'aide"
```

L'application entre en **mode SOS** (fond rouge), une vibration forte de 1000ms se déclenche, et le message vocal est prononcé :

```
"SOS déclenché, les secours ont été alertés, restez en ligne."
```

---

### Étape 8 — Annuler une action

Appui long sur le bouton micro, ou dire :

```
"Stop" / "Annuler" / "Arrête"
```

---

!!! tip "Interface Swagger"
    Pour tester les endpoints directement sans l'application mobile, ouvrir `http://localhost:8000/docs` dans un navigateur.
