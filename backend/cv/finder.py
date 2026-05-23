# cv/finder.py
from cv.core.model_loader import get_model_coco, get_model_custom
from cv.core.depth_loader import get_depth_model
from cv.detector import estimer_distance
from PIL import Image
import numpy as np
import cv2


# Classes gérées par le modèle custom
CLASSES_CUSTOM = {"fire", "hunman-fire", "stairs", "knife"}


# ================================
# GÉNÉRATION D'INSTRUCTION VOCALE
# ================================

def _generer_instruction(target: str, position: str, distance: str) -> tuple[str, bool]:
    """
    Génère une instruction vocale selon la position et la distance.
    Retourne (message, reached).
    reached=True quand l'objet est atteint.
    """
    # Objet atteint
    if distance == "tres proche" and position == "centre":
        return f"Vous y etes. {target} est juste devant vous, tendez la main.", True

    # Guidage selon position
    if position == "extreme_gauche":
        msg = f"Tournez franchement a gauche vers {target}."

    elif position == "legerement_gauche":
        if distance == "loin":
            msg = f"Tournez legerement a gauche et avancez vers {target}."
        else:
            msg = f"Tournez un peu a gauche, {target} est presque la."

    elif position == "centre":
        if distance == "loin":
            msg = f"{target} est droit devant vous, avancez."
        elif distance == "proche":
            msg = f"Continuez tout droit, {target} est presque a portee."
        else:
            msg = f"Tendez la main, {target} est juste devant vous."

    elif position == "legerement_droite":
        if distance == "loin":
            msg = f"Tournez legerement a droite et avancez vers {target}."
        else:
            msg = f"Tournez un peu a droite, {target} est presque la."

    else:  # extreme_droite
        msg = f"Tournez franchement a droite vers {target}."

    return msg, False


# ================================
# RECHERCHE D'OBJET
# ================================

def find_object(image_path: str, target: str) -> dict:
    """
    Cherche un objet cible dans l'image et retourne
    une instruction vocale pour guider l'utilisateur.

    Appelé par Flutter toutes les 5 secondes avec une nouvelle frame.

    Retourne toujours un dict avec :
    - found       : bool
    - tts_message : instruction à lire via TTS
    - reached     : bool (True = objet atteint, Flutter arrête la boucle)
    - details     : infos de détection (si trouvé)
    """
    # ── Choix du modèle selon la cible ────────────────────────────────────
    yolo  = get_model_custom() if target.lower() in CLASSES_CUSTOM else get_model_coco()
    depth = get_depth_model()

    # ── Carte de profondeur ───────────────────────────────────────────────
    pil_image = Image.open(image_path).convert("RGB")
    depth_raw = depth(pil_image)["depth"]
    depth_map = cv2.GaussianBlur(
        np.array(depth_raw).astype(np.float32), (15, 15), 0
    )

    # ── Détection YOLO ────────────────────────────────────────────────────
    results   = yolo(image_path, verbose=False)
    best      = None
    best_conf = 0.0

    for r in results:
        img_w = r.orig_shape[1]

        for box in r.boxes:
            cls_name = r.names[int(box.cls)]
            conf     = float(box.conf)

            if target.lower() not in cls_name.lower():
                continue
            if conf < 0.4 or conf <= best_conf:
                continue

            best_conf = conf
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]

            # ── Position horizontale (5 zones) ────────────────────────────
            cx_ratio = (x1 + x2) / 2 / img_w

            if cx_ratio < 0.20:
                position = "extreme_gauche"
            elif cx_ratio < 0.40:
                position = "legerement_gauche"
            elif cx_ratio < 0.60:
                position = "centre"
            elif cx_ratio < 0.80:
                position = "legerement_droite"
            else:
                position = "extreme_droite"

            # ── Distance via Depth Anything ───────────────────────────────
            distance_label, depth_score = estimer_distance(
                depth_map, x1, y1, x2, y2
            )

            # ── Conversion types NumPy → Python natif ─────────────────────
            best = {
                "objet":       cls_name,
                "confiance":   float(round(conf, 2)),
                "position":    position,
                "distance":    distance_label,
                "depth_score": float(depth_score),
                "x1": int(x1), "y1": int(y1),
                "x2": int(x2), "y2": int(y2)
            }

    # ── Résultat ──────────────────────────────────────────────────────────
    if best is None:
        return {
            "found":       False,
            "tts_message": f"Je ne vois pas {target}. Tournez lentement.",
            "reached":     False,
            "details":     None
        }

    instruction, reached = _generer_instruction(
        target, best["position"], best["distance"]
    )

    return {
        "found":       True,
        "tts_message": instruction,
        "reached":     reached,
        "details":     best
    }