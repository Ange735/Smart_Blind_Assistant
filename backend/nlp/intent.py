# nlp/intent.py
import json
import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os

from nlp.model_loader import get_model, get_spacy_model

# ── Chargement des modèles ────────────────────────────────────────────────────
model     = get_model()
nlp_spacy = get_spacy_model()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, 'intents.json'), 'r', encoding='utf-8') as f:
    intents = json.load(f)

intent_embeddings = {}
for intent, examples in intents.items():
    intent_embeddings[intent] = model.encode(examples)


# ================================
# CLASSES YOLO COCO
# Liste fixe des 80 classes détectables — encodée une seule fois
# ================================

YOLO_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train",
    "truck", "boat", "traffic light", "fire hydrant", "stop sign",
    "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep",
    "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
    "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard",
    "sports ball", "kite", "baseball bat", "baseball glove", "skateboard",
    "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork",
    "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
    "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
    "couch", "potted plant", "bed", "dining table", "toilet", "tv",
    "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave",
    "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase",
    "scissors", "teddy bear", "hair drier", "toothbrush",
    # Classes custom
    "fire", "knife", "stairs", "hunman-fire"
]

# Encodage des classes YOLO une seule fois au démarrage
print("[NLP] Encodage des classes YOLO...")
_yolo_embeddings = model.encode(YOLO_CLASSES)
print("[NLP] Classes YOLO encodées ✅")


# ================================
# PIÈCES CONNUES
# Petite liste uniquement pour distinguer NAVIGATE de FIND_OBJECT
# ================================

PIECES = {
    "cuisine", "salon", "chambre", "couloir",
    "salle de bain", "bureau", "entrée",
    "toilettes", "jardin", "terrasse"
}


# ================================
# MAPPING YOLO SÉMANTIQUE
# Trouve la classe YOLO la plus proche sémantiquement
# Aucun mapping manuel — le modèle fait tout
# ================================

def _trouver_classe_yolo(entite: str, seuil: float = 0.45) -> str | None:
    """
    Trouve la classe YOLO la plus proche de l'entité via similarité cosinus.
    Le modèle multilingue gère French→English automatiquement.

    "frigo"  → "refrigerator"
    "télé"   → "tv"
    "chien"  → "dog"
    "robot"  → None (score trop faible)
    """
    if not entite:
        return None

    entite_embedding = model.encode([entite])
    similarities     = cosine_similarity(entite_embedding, _yolo_embeddings)[0]
    best_idx         = int(np.argmax(similarities))
    best_score       = float(similarities[best_idx])

    if best_score >= seuil:
        return YOLO_CLASSES[best_idx]

    return None


# ================================
# EXTRACTION D'ENTITÉ — spaCy
# ================================

def _extraire_entite_spacy(phrase: str, categories: list) -> dict:
    """
    Extrait l'entité via analyse grammaticale.
    spaCy lemmatise automatiquement — pas besoin d'ENTITY_CANONICAL.
    """
    if nlp_spacy is None or not categories:
        return {}

    doc = nlp_spacy(phrase.lower())

    # ── Stratégie 1 : COD direct du verbe ────────────────────────────
    for token in doc:
        if token.dep_ in ("obj", "dobj") and token.pos_ in ("NOUN", "PROPN"):
            return _construire_entite(token.lemma_, categories)

    # ── Stratégie 2 : nom après déterminant ──────────────────────────
    for i, token in enumerate(doc):
        if token.pos_ == "DET" and i + 1 < len(doc):
            next_tok = doc[i + 1]
            if next_tok.pos_ in ("NOUN", "PROPN"):
                return _construire_entite(next_tok.lemma_, categories)

    return {}


def _construire_entite(value: str, categories: list) -> dict:
    """
    Construit le dict entité :
    - Si c'est une pièce → type pièce
    - Sinon → type objet + matching YOLO sémantique
    """
    # Vérification pièce
    if "pièce" in categories:
        for piece in PIECES:
            if piece in value or value in piece:
                return {
                    "type":       "pièce",
                    "value":      value,
                    "yolo_class": None,
                    "detectable": False
                }

    # Objet → matching YOLO sémantique
    if "objet" in categories:
        yolo_class = _trouver_classe_yolo(value)
        return {
            "type":       "objet",
            "value":      value,
            "yolo_class": yolo_class or value,
            "detectable": True
        }

    return {}


def extract_entity(phrase: str, categories: list) -> dict:
    """Point d'entrée unique — délègue à spaCy."""
    if not categories:
        return {}
    return _extraire_entite_spacy(phrase, categories)


# ================================
# FALLBACK SPACY — intent par verbe
# ================================

VERBES_FIND = {
    "trouver", "chercher", "retrouver", "voir",
    "perdre", "localiser", "repérer", "rechercher"
}
VERBES_NAVIGATE = {
    "aller", "guider", "emmener", "conduire",
    "amener", "diriger", "mener", "rejoindre"
}
VERBES_LOCATE = {
    "situer", "trouver", "être", "se trouver"
}

def _detecter_intent_spacy(phrase: str) -> str | None:
    if nlp_spacy is None:
        return None

    doc = nlp_spacy(phrase.lower())

    for token in doc:
        if token.pos_ == "VERB":
            lemme = token.lemma_
            if lemme in VERBES_FIND:
                return "FIND_OBJECT"
            if lemme in VERBES_NAVIGATE:
                return "NAVIGATE"
            if lemme in VERBES_LOCATE:
                if any(t.text in ["où", "suis", "situe"] for t in doc):
                    return "LOCATE_ROOM"

    return None


# ================================
# PRÉTRAITEMENT
# ================================

def _nettoyer_phrase(phrase: str) -> str:
    phrase = phrase.lower().strip()
    phrase = re.sub(r'\s+', ' ', phrase)
    return phrase


# ================================
# DÉTECTION D'INTENTION — architecture combinée
# ================================

INTENT_ENTITY_MAP = {
    "FIND_OBJECT": ["objet"],
    "NAVIGATE":    ["pièce", "objet"],
    "LOCATE_ROOM": [],
    "SOS":         [],
    "UNKNOWN":     [],
}

def detect_intent(
    phrase:     str,
    threshold:  float = 0.72,
    min_margin: float = 0.05
) -> dict:
    phrase_originale = phrase
    phrase_nettoyee  = _nettoyer_phrase(phrase)

    embedding = model.encode([phrase_nettoyee])

    scores = {}
    for intent, embeddings in intent_embeddings.items():
        sims           = cosine_similarity(embedding, embeddings)
        scores[intent] = float(np.max(sims))

    sorted_scores              = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_intent, best_score    = sorted_scores[0]
    second_score               = sorted_scores[1][1] if len(sorted_scores) > 1 else 0.0
    margin                     = best_score - second_score

    confident = best_score >= threshold and margin >= min_margin
    source    = "sentence_transformer"

    # ── Niveau 1 : SentenceTransformer ───────────────────────────────
    if confident:
        final_intent = best_intent

    # ── Niveau 2 : Fallback spaCy (verbe) ────────────────────────────
    else:
        spacy_intent = _detecter_intent_spacy(phrase_nettoyee)

        if spacy_intent:
            final_intent = spacy_intent
            confident    = True
            source       = "spacy_verbe"

        # ── Niveau 3 : Fallback entité ────────────────────────────────
        else:
            entity_objet = _extraire_entite_spacy(phrase_nettoyee, ["objet"])
            entity_piece = _extraire_entite_spacy(phrase_nettoyee, ["pièce"])

            if entity_objet:
                final_intent = "FIND_OBJECT"
                confident    = True
                source       = "fallback_entite"
            elif entity_piece:
                final_intent = "NAVIGATE"
                confident    = True
                source       = "fallback_entite"
            else:
                final_intent = "UNKNOWN"
                source       = "unknown"

    # ── Extraction d'entité selon l'intent ───────────────────────────
    categories = INTENT_ENTITY_MAP.get(final_intent, [])
    entity     = extract_entity(phrase_nettoyee, categories)

    return {
        "intent":           final_intent,
        "score":            round(best_score, 3),
        "margin":           round(margin, 3),
        "confident":        confident,
        "source":           source,
        "entity":           entity,
        "phrase_originale": phrase_originale,
        "phrase_nettoyee":  phrase_nettoyee,
    }