# Limitations actuelles

## Tableau des limitations

| Limitation | Impact | Gravité |
|------------|--------|---------|
| YOLO ne détecte pas clés, lunettes, portefeuille | `finder` retourne « non trouvé » | ⚠️ Important |
| Depth Anything V2 imprécis pour 2 objets proches | Instructions légèrement approximatives | 🟡 Modéré |
| STT nécessite Google API (connexion internet) | Pas de reconnaissance offline | ⚠️ Important |
| spaCy `fr_core_news_sm` — modèle léger | Lemmatisation parfois imprécise | 🟢 Faible |
| SOS simulé (pas d'appel réel) | Démo uniquement | ⚠️ Important en production |
| Heading boussole non intégré au pipeline | Navigation sans orientation réelle | ⚠️ Important |

---

## Détail des limitations critiques

### Objets personnels non détectés par YOLO

Le modèle YOLO COCO ne couvre pas les petits objets personnels. Les demandes comme *« cherche mes clés »* retourneront *« objet non trouvé dans l'image »*.

**Workaround temporaire** : utiliser des descriptions de position générale — *« est-ce qu'il y a quelque chose sur la table »*.

---

### STT dépendant d'internet

Le package `speech_to_text` utilise l'API Google Speech par défaut. En l'absence de connexion internet, la reconnaissance vocale est non fonctionnelle.

**Impact** : le système est inutilisable hors connexion, ce qui est problématique pour l'autonomie de l'utilisateur.

---

### Navigation sans boussole

Le champ `heading` (orientation de l'utilisateur) est prévu dans l'API `/navigate` mais n'est pas encore intégré dans le flux Flutter. Les instructions de navigation sont générées en supposant une orientation fixe, ce qui peut induire des erreurs (*« tournez à droite »* alors que l'utilisateur est déjà orienté dans la bonne direction).

---

### SOS non connecté à de vrais services d'urgence

Le module SOS écrit uniquement dans les logs et simule un appel. En l'état, il ne peut pas être utilisé dans un contexte réel d'urgence.
