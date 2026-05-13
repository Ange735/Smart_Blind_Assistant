# cv/localizer.py
from cv.core.model_loader import get_model_coco


# ================================
# SIGNATURES DES PIÈCES
# Uniquement des classes COCO réelles détectables par YOLOv8
# ================================

ROOM_SIGNATURES = {
    "salon":         {"couch", "tv", "remote", "potted plant", "dining table"},
    "cuisine":       {"refrigerator", "oven", "microwave", "sink", "bottle",
                      "bowl", "cup", "wine glass", "fork", "knife", "spoon"},
    "chambre":       {"bed", "clock", "cell phone"},
    "salle de bain": {"toilet", "sink", "toothbrush", "hair drier"},
    "bureau":        {"laptop", "keyboard", "mouse", "tv", "book", "scissors"},
    "couloir":       {"suitcase", "backpack", "umbrella"},
}

# Poids des objets très caractéristiques d'une pièce
POIDS = {
    "bed":          4,
    "toilet":       4,
    "refrigerator": 4,
    "couch":        3,
    "tv":           2,
    "oven":         3,
    "microwave":    2,
    "laptop":       2,
    "keyboard":     2,
    "toothbrush":   3,
    "hair drier":   3,
}


# ================================
# LOCALISATION
# ================================

def localize(image_path: str) -> dict:
    """
    Analyse l'image et retourne la pièce détectée
    avec un message vocal prêt pour le TTS.

    Retourne :
    - piece           : nom de la pièce détectée
    - score           : score pondéré par confiance
    - confiance_pct   : pourcentage de confiance (0-100)
    - objets_detectes : liste des objets vus par YOLO
    - tts_message     : message vocal prêt pour Flutter
    """
    model   = get_model_coco()
    results = model(image_path, verbose=False)

    # ── Récupère les objets détectés avec confiance >= 0.4 ────────────────
    detected_conf = {}
    for r in results:
        for box in r.boxes:
            conf     = float(box.conf)
            cls_name = r.names[int(box.cls)]
            if conf >= 0.4:
                if cls_name not in detected_conf or conf > detected_conf[cls_name]:
                    detected_conf[cls_name] = conf

    if not detected_conf:
        return {
            "piece":           "inconnue",
            "score":           0,
            "confiance_pct":   0,
            "objets_detectes": [],
            "tts_message":     "Je ne reconnais pas cette piece."
        }

    # ── Calcule le score de chaque pièce (pondéré par confiance) ──────────
    scores = {}
    for room, signature in ROOM_SIGNATURES.items():
        score = 0
        for obj in signature:
            if obj in detected_conf:
                poids  = POIDS.get(obj, 1)
                score += poids * detected_conf[obj]
        scores[room] = score

    best_room  = max(scores, key=scores.get)
    best_score = scores[best_room]

    if best_score == 0:
        return {
            "piece":           "inconnue",
            "score":           0,
            "confiance_pct":   0,
            "objets_detectes": list(detected_conf.keys()),
            "tts_message":     "Je ne reconnais pas cette piece."
        }

    # ── Calcule le pourcentage de confiance ───────────────────────────────
    max_possible = sum(POIDS.get(obj, 1) for obj in ROOM_SIGNATURES[best_room])
    confiance    = min(100, int((best_score / max_possible) * 100))

    # ── Message TTS selon confiance ───────────────────────────────────────
    if confiance >= 70:
        tts_message = f"Vous etes dans la {best_room}."
    elif confiance >= 40:
        tts_message = f"Je pense que vous etes dans la {best_room}."
    else:
        tts_message = f"Vous etes peut-etre dans la {best_room}, je ne suis pas certain."

    return {
        "piece":           best_room,
        "score":           round(best_score, 2),
        "confiance_pct":   confiance,
        "objets_detectes": list(detected_conf.keys()),
        "tts_message":     tts_message
    }