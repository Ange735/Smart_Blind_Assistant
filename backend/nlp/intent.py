import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os

from nlp.model_loader import get_model

model = get_model()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, 'intents.json'), 'r', encoding='utf-8') as f:
    intents = json.load(f)

intent_embeddings = {}
for intent, examples in intents.items():
    intent_embeddings[intent] = model.encode(examples)

ENTITIES = {
    "objet": [
        "clés", "clé", "clefs", "clef",
        "lunettes", "lunette",
        "téléphone", "portable", "smartphone",
        "portefeuille",
        "chaussures", "chaussure",
        "sac", "télécommande", "canne",
        "montre", "médicaments", "médicament",
    ],
    "pièce": [
        "cuisine", "salon", "living", "chambre",
        "salle de bain", "salle de bains", "douche",
        "entrée", "couloir", "toilettes", "wc",
        "bureau", "jardin", "terrasse",
    ]
}

ENTITY_CANONICAL = {
    "clé": "clés", "clefs": "clés", "clef": "clés",
    "lunette": "lunettes",
    "portable": "téléphone", "smartphone": "téléphone",
    "chaussure": "chaussures",
    "salle de bains": "salle de bain", "douche": "salle de bain",
    "living": "salon",
    "wc": "toilettes",
    "médicament": "médicaments",
}

# Mapping entité NLP → classe YOLO (None = pas détectable visuellement)
ENTITY_TO_YOLO = {
    "téléphone":     "cell phone",
    "télécommande":  "remote",
    "sac":           "backpack",
    "toilettes":     "toilet",
    "lunettes":      None,
    "clés":          None,
    "chaussures":    None,
    "portefeuille":  None,
    "montre":        None,
    "médicaments":   None,
    "canne":         None,
    # pièces → gérées par localizer, pas par finder
    "cuisine":       None,
    "salon":         None,
    "chambre":       None,
    "salle de bain": None,
    "couloir":       None,
    "bureau":        None,
    "entrée":        None,
    "jardin":        None,
    "terrasse":      None,
}

# Catégorie d'entité attendue selon l'intent
INTENT_ENTITY_MAP = {
    "FIND_OBJECT": ["objet"],
    "NAVIGATE":    ["pièce"],
    "LOCATE_ROOM": [],
    "SOS":         [],
    "UNKNOWN":     [],
}


def extract_entity(phrase: str, categories: list) -> dict:
    if not categories:
        return {}

    phrase_lower = phrase.lower()
    best_match = None
    best_len = 0

    for category in categories:
        for mot in ENTITIES.get(category, []):
            if mot in phrase_lower and len(mot) > best_len:
                best_match = (category, mot)
                best_len = len(mot)

    if best_match:
        category, value = best_match
        value = ENTITY_CANONICAL.get(value, value)
        yolo_class = ENTITY_TO_YOLO.get(value)
        detectable = yolo_class is not None
        return {
            "type":       category,
            "value":      value,
            "yolo_class": yolo_class,
            "detectable": detectable,
        }

    return {}


def detect_intent(phrase: str, threshold: float = 0.72, min_margin: float = 0.05) -> dict:
    embedding = model.encode([phrase])

    scores = {}
    for intent, embeddings in intent_embeddings.items():
        sims = cosine_similarity(embedding, embeddings)
        scores[intent] = float(np.max(sims))

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_intent, best_score = sorted_scores[0]
    second_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0.0
    margin = best_score - second_score

    confident = best_score >= threshold and margin >= min_margin
    if not confident:
        best_intent = "UNKNOWN"

    categories = INTENT_ENTITY_MAP.get(best_intent, [])
    entity = extract_entity(phrase, categories)

    return {
        "intent":    best_intent,
        "score":     round(best_score, 3),
        "margin":    round(margin, 3),
        "confident": confident,
        "entity":    entity,
        "phrase":    phrase,
    }