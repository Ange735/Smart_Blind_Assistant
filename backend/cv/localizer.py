# cv/localizer.py
from cv.core.model_loader import get_model

ROOM_SIGNATURES = {
    "salon":       {"couch", "tv", "remote", "coffee table", "potted plant"},
    "cuisine":     {"refrigerator", "oven", "sink", "bottle", "bowl", "cup", "microwave"},
    "chambre":     {"bed", "clock", "laptop"},
    "salle de bain": {"toilet", "sink", "toothbrush"},
    "bureau":      {"laptop", "keyboard", "mouse", "monitor"},
    "couloir":     {"door", "suitcase", "backpack"},
}

# poids des objets dominants (signaux très forts)
POIDS = {
    "bed": 3,
    "couch": 2,
    "tv": 2,
    "refrigerator": 3,
    "toilet": 3,
    "laptop": 2,
}

def localize(image) -> dict:
    model = get_model()
    results = model(image, verbose=False)

    # récupère les classes détectées avec confiance >= 0.4
    detected = {
        r.names[int(box.cls)]
        for r in results
        for box in r.boxes
        if float(box.conf) >= 0.4
    }

    if not detected:
        return {"piece": "inconnue", "score": 0, "objets_detectes": []}

    # calcule le score de chaque pièce
    scores = {}
    for room, signature in ROOM_SIGNATURES.items():
        score = 0
        for obj in detected & signature:
            score += POIDS.get(obj, 1)
        scores[room] = score

    best_room = max(scores, key=scores.get)
    best_score = scores[best_room]

    # si aucun objet ne correspond
    if best_score == 0:
        return {"piece": "inconnue", "score": 0, "objets_detectes": list(detected)}

    return {
        "piece": best_room,
        "score": best_score,
        "objets_detectes": list(detected)
    }