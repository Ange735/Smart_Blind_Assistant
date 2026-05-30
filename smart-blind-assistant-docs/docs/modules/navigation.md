# Module Navigation

## Principe

Le module navigation guide l'utilisateur de sa position actuelle vers une pièce cible. Contrairement à la navigation GPS, ce système utilise un **graphe de connexions** défini par l'aidant et la caméra pour détecter la position actuelle.

---

## Modélisation de la maison

La maison est modélisée comme un **graphe orienté** :
- **Nœuds** : les pièces
- **Arêtes** : les connexions entre pièces, avec leur direction absolue

```json
{
  "rooms": ["salon", "cuisine", "chambre", "salle_de_bain", "bureau"],
  "connections": [
    {"from": "salon",   "to": "cuisine",       "angle": 90},
    {"from": "salon",   "to": "chambre",        "angle": 0},
    {"from": "chambre", "to": "salle_de_bain",  "angle": 90},
    {"from": "salon",   "to": "bureau",         "angle": 270}
  ]
}
```

Les angles absolus permettent de calculer dynamiquement **gauche/droite/avancez** selon l'orientation réelle de l'utilisateur (boussole du smartphone).

---

## Algorithme de recherche de chemin — BFS

!!! question "Pourquoi BFS et non Dijkstra ?"
    Dijkstra est optimisé pour les graphes pondérés où les arêtes ont des distances différentes. Dans une maison, toutes les connexions ont le même « coût » — passer d'une pièce à une autre demande le même effort. **BFS donne le même résultat optimal** avec une implémentation plus simple et plus efficace.

La position de départ est **détectée automatiquement** par `localizer.py` depuis la caméra. L'utilisateur dit simplement *« emmène-moi à la cuisine »* sans préciser où il se trouve.

---

## Instructions dynamiques selon l'orientation

Le système adapte les instructions selon le `heading` retourné par la boussole du smartphone :

| Heading utilisateur | Angle cible maison | Instruction générée |
|---------------------|-------------------|---------------------|
| 90° (regarde Est) | 0° (Nord) | « Tournez à gauche. » |
| 90° (regarde Est) | 90° (Est) | « Avancez. » |
| 90° (regarde Est) | 180° (Sud) | « Tournez à droite. » |
| 0° (regarde Nord) | 90° (Est) | « Tournez à droite. » |

### Formule de calcul

```python
diff = (target_angle - heading + 360) % 360

if diff < 30 or diff > 330:
    instruction = "Avancez"
elif diff < 180:
    instruction = "Tournez à droite"
else:
    instruction = "Tournez à gauche"
```

---

## Cas particuliers

| Situation | Comportement |
|-----------|-------------|
| Pièce actuelle inconnue | Réponse claire avec TTS approprié : « Je ne sais pas où vous êtes, pouvez-vous décrire ce que vous voyez ? » |
| Maison non configurée | Chargement automatique de `house_default.json` |
| Destination = position actuelle | « Vous êtes déjà dans [pièce]. » |
| Chemin impossible | « Je n'ai pas trouvé de chemin vers [pièce]. » |
