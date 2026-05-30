# Module NLP — Compréhension du langage

## Défi de la compréhension vocale

Le module NLP doit comprendre des **phrases françaises naturelles et variées**, extraire l'intention de l'utilisateur et identifier l'objet ou le lieu mentionné — sans forcer l'utilisateur à mémoriser des commandes spécifiques.

---

## Architecture combinée à trois niveaux

| Niveau | Système | Rôle |
|--------|---------|------|
| 1 | SentenceTransformer (MiniLM) | Similarité sémantique avec les exemples — très efficace pour les formulations connues |
| 2 | spaCy `fr_core_news_sm` | Analyse grammaticale — détecte le verbe d'intention indépendamment de l'objet |
| 3 | Fallback entité | Si ni ST ni spaCy : détecte un nom d'objet ou de lieu dans la phrase |

### Exemple illustratif

```
"Je ne retrouve pas mon lit"
  │
  ├── SentenceTransformer score = 0.64 (< seuil 0.72 → insuffisant)
  │
  ├── spaCy détecte verbe "retrouver" → FIND_OBJECT ✓
  │
  └── Extraction entité : "lit" → classe YOLO "bed" (score 0.89)
```

---

## SentenceTransformer — Compréhension sémantique

Le modèle `paraphrase-multilingual-MiniLM-L12-v2` transforme une phrase en **vecteur mathématique** représentant son sens. La similarité cosinus entre ce vecteur et les exemples de chaque intention détermine l'intention la plus probable.

### Seuils de classification

| Paramètre | Valeur | Rôle |
|-----------|--------|------|
| Seuil de score | **0.72** | En dessous, l'intention n'est pas assez certaine |
| Seuil de marge | **0.05** | L'écart entre la 1ère et 2ème intention doit être suffisant |

!!! bug "Bug corrigé : `bonjour → NAVIGATE`"
    Le seuil initial à 0.5 classait « bonjour » comme NAVIGATE avec un score de 0.67. Relevé à **0.72**, il retourne correctement `UNKNOWN`.

---

## spaCy — Analyse grammaticale

| Verbes détectés | Intention déduite | Exemple |
|-----------------|-------------------|---------|
| trouver, chercher, retrouver, perdre… | `FIND_OBJECT` | « je ne retrouve pas mon lit » |
| aller, guider, emmener, conduire… | `NAVIGATE` | « guide-moi vers la cuisine » |
| situer, être (+ où)… | `LOCATE_ROOM` | « je suis où là » |

---

## Extraction d'entité — Approche sémantique sans liste

L'extraction d'entité se fait en **3 étapes** sans dictionnaire de traduction :

| Étape | Système | Action |
|-------|---------|--------|
| 1 | spaCy (lemmatisation) | Extrait le nom COD de la phrase |
| 2 | SentenceTransformer | Calcule la similarité entre l'entité et les 84 classes YOLO |
| 3 | Matching | Retourne la classe YOLO la plus proche si score ≥ 0.45 |

### Exemples

| Phrase utilisateur | Entité extraite | Classe YOLO trouvée |
|-------------------|-----------------|---------------------|
| « je cherche la tv » | tv | tv (score ~0.95) |
| « je cherche mon frigo » | frigo | refrigerator (score ~0.72) |
| « je cherche mon chien » | chien | dog (score ~0.85) |
| « guide-moi vers la cuisine » | cuisine | pièce (pas de classe YOLO) |
| « je cherche mon robot » | robot | None (score trop faible) |

!!! success "Avantage multilingue"
    Le modèle multilingue comprend que « frigo » en français correspond à « refrigerator » en anglais (les classes YOLO sont en anglais). Aucun dictionnaire de traduction n'est nécessaire — la **similarité sémantique cross-linguale** gère automatiquement cette correspondance.

---

## Champ `source` — Traçabilité

| Valeur | Signification |
|--------|---------------|
| `sentence_transformer` | SentenceTransformer confiant — résultat fiable |
| `spacy_verbe` | ST insuffisant, spaCy a pris le relais via le verbe |
| `fallback_entite` | Ni ST ni spaCy — un objet ou lieu a été trouvé dans la phrase |
| `unknown` | Aucun niveau n'a pu déterminer l'intention |
