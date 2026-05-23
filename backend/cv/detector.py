# cv/detector.py
from cv.core.model_loader import get_model_coco, get_model_custom
from cv.core.depth_loader import get_depth_model
from PIL import Image
import numpy as np
import cv2
import concurrent.futures


# ================================
# ESTIMATION DE DISTANCE
# ================================

def estimer_distance(depth_map, x1, y1, x2, y2):
    depth_lisse = cv2.GaussianBlur(depth_map.astype(np.float32), (15, 15), 0)
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    marge = 20
    zone = depth_lisse[
        max(0, cy - marge):cy + marge,
        max(0, cx - marge):cx + marge
    ]
    valeur = float(zone.mean()) if zone.size > 0 else float(depth_lisse[cy, cx])
    d_min = depth_lisse.min()
    d_max = depth_lisse.max()
    valeur_norm = (valeur - d_min) / (d_max - d_min) if d_max != d_min else 0.5

    if valeur_norm > 0.65:
        label = "tres proche"
    elif valeur_norm > 0.35:
        label = "proche"
    else:
        label = "loin"

    return label, round(float(valeur_norm), 3)


# ================================
# SUPPRESSION DES DOUBLONS
# ================================

def _iou(a, b):
    x1 = max(a["x1"], b["x1"])
    y1 = max(a["y1"], b["y1"])
    x2 = min(a["x2"], b["x2"])
    y2 = min(a["y2"], b["y2"])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    if inter == 0:
        return 0
    aire_a = (a["x2"] - a["x1"]) * (a["y2"] - a["y1"])
    aire_b = (b["x2"] - b["x1"]) * (b["y2"] - b["y1"])
    return inter / (aire_a + aire_b - inter)

def _supprimer_doublons(obstacles: list, iou_threshold: float = 0.5) -> list:
    if not obstacles:
        return obstacles
    obstacles = sorted(obstacles, key=lambda x: x["confiance"], reverse=True)
    gardes = []
    for obs in obstacles:
        doublon = False
        for garde in gardes:
            if _iou(obs, garde) > iou_threshold:
                doublon = True
                break
        if not doublon:
            gardes.append(obs)
    return gardes


# ================================
# GÉNÉRATION D'ALERTE VOCALE
# ================================

OBJET_FR = {
    "person":        "une personne",
    "chair":         "une chaise",
    "bed":           "un lit",
    "couch":         "un canape",
    "tv":            "une television",
    "laptop":        "un ordinateur",
    "refrigerator":  "un refrigerateur",
    "oven":          "un four",
    "sink":          "un evier",
    "toilet":        "des toilettes",
    "vase":          "un vase",
    "cup":           "une tasse",
    "bottle":        "une bouteille",
    "bowl":          "un bol",
    "knife":         "un couteau",
    "potted plant":  "une plante",
    "backpack":      "un sac a dos",
    "suitcase":      "une valise",
    "bicycle":       "un velo",
    "dog":           "un chien",
    "cat":           "un chat",
    "cell phone":    "un telephone",
    "remote":        "une telecommande",
    "mouse":         "une souris",
    "keyboard":      "un clavier",
    "clock":         "une horloge",
    "mirror":        "un miroir",
    "dining table":  "une table",
    "door":          "une porte",
    "stairs":        "des escaliers",
    "fire":          "du feu",
    "hunman-fire":   "une personne en feu",
}

# Classes dangereuses → alerte peu importe la distance
CLASSES_DANGER = {"fire", "hunman-fire", "knife", "stairs"}

# Priorités des alertes
PRIORITE = {
    "hunman-fire": 5,
    "fire":        4,
    "knife":       3,
    "stairs":      2,
    "tres proche": 2,
    "proche":      1,
}

def _generer_alerte(objet_fr, position, distance, cls_name=""):
    if position == "centre":
        direction = "droit devant vous"
    elif position == "gauche":
        direction = "a votre gauche"
    else:
        direction = "a votre droite"

    # ── Dangers permanents (peu importe distance) ─────────────────────────
    if cls_name == "hunman-fire":
        if distance == "tres proche":
            return f"Danger extreme ! Personne en feu {direction}, fuyez immediatement !"
        elif distance == "proche":
            return f"Danger ! Personne en feu {direction}, eloignez-vous !"
        else:
            return f"Attention ! Personne en feu detectee {direction}."

    if cls_name == "fire":
        if distance == "tres proche":
            return f"Danger extreme ! Feu {direction}, reculez immediatement !"
        elif distance == "proche":
            return f"Danger ! Feu detecte {direction}, eloignez-vous !"
        else:
            return f"Attention ! Feu detecte {direction}."

    if cls_name == "knife":
        if distance == "tres proche":
            return f"Danger extreme ! Couteau {direction}, reculez immediatement !"
        elif distance == "proche":
            return f"Danger ! Couteau detecte {direction}, soyez prudent !"
        else:
            return f"Attention ! Couteau detecte {direction}."

    if cls_name == "stairs":
        if distance == "tres proche":
            return f"Attention ! Escaliers {direction}, arretez-vous !"
        elif distance == "proche":
            return f"Escaliers detectes {direction}, avancez prudemment."
        else:
            return f"Escaliers detectes {direction}."

    # ── Obstacles normaux → alerte seulement si proche ou tres proche ─────
    if distance == "loin":
        return None

    if distance == "tres proche":
        return f"Attention ! {objet_fr} {direction}, arretez-vous !"
    else:
        return f"Obstacle detecte, {objet_fr} {direction}."


# ================================
# DÉTECTEUR D'OBSTACLES
# ================================

def _run_yolo(model, image_path):
    return model(image_path, verbose=False)

class ObstacleDetector:
    def __init__(self):
        self.yolo_coco   = get_model_coco()
        self.yolo_custom = get_model_custom()
        self.depth       = get_depth_model()

    def detect(self, image_path: str) -> dict:
        # ── Carte de profondeur ───────────────────────────────────────────
        pil_image = Image.open(image_path).convert("RGB")
        depth_raw = self.depth(pil_image)["depth"]
        depth_map = np.array(depth_raw)

        # ── 2 modèles en parallèle ────────────────────────────────────────
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_coco   = executor.submit(_run_yolo, self.yolo_coco, image_path)
            future_custom = executor.submit(_run_yolo, self.yolo_custom, image_path)
            results_coco   = future_coco.result()
            results_custom = future_custom.result()

        obstacles = []

        # ── Traitement des résultats ──────────────────────────────────────
        for results in [results_coco, results_custom]:
            for r in results:
                img_width = r.orig_shape[1]

                for box in r.boxes:
                    cls_name = r.names[int(box.cls)]
                    conf     = float(box.conf)

                    if conf < 0.4:
                        continue

                    x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]

                    cx = (x1 + x2) / 2
                    if cx < img_width / 3:
                        position = "gauche"
                    elif cx < 2 * img_width / 3:
                        position = "centre"
                    else:
                        position = "droite"

                    distance_label, depth_valeur = estimer_distance(
                        depth_map, x1, y1, x2, y2
                    )

                    objet_fr = OBJET_FR.get(cls_name, cls_name)
                    alerte   = _generer_alerte(objet_fr, position, distance_label, cls_name)

                    # ── Conversion types NumPy → Python natif ─────────────
                    obstacles.append({
                        "objet":       cls_name,
                        "objet_fr":    objet_fr,
                        "confiance":   float(round(conf, 2)),
                        "position":    position,
                        "distance":    distance_label,
                        "depth_score": float(depth_valeur),
                        "x1": int(x1), "y1": int(y1),
                        "x2": int(x2), "y2": int(y2),
                        "alerte":      alerte,
                    })

        # ── Suppression des doublons ──────────────────────────────────────
        obstacles = _supprimer_doublons(obstacles)

        # ── Génération des alertes après déduplication ────────────────────
        alertes = []
        for obs in obstacles:
            if obs["alerte"]:
                if obs["objet"] in PRIORITE:
                    priorite = PRIORITE[obs["objet"]]
                else:
                    priorite = PRIORITE.get(obs["distance"], 0)

                if obs["distance"] == "tres proche":
                    priorite += 1

                alertes.append({
                    "message":  obs["alerte"],
                    "priorite": priorite,
                    "objet":    obs["objet"],
                    "position": obs["position"],
                    "distance": obs["distance"],
                })
            del obs["alerte"]

        # ── Tri par priorité décroissante ─────────────────────────────────
        alertes.sort(key=lambda a: a["priorite"], reverse=True)

        # ── Message TTS = tous les messages concaténés par ordre priorité ─
        tts_message = None
        if alertes:
            tts_message = "\n".join([a["message"] for a in alertes])

        return {
            "obstacles":   obstacles,
            "alertes":     alertes,
            "tts_message": tts_message
        }