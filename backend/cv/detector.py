# detector.py
from cv.core.model_loader import get_model

TAILLE_REF = {
    "person": 0.15, "chair": 0.08, "bed": 0.25, "couch": 0.20,
    "tv": 0.12, "laptop": 0.08, "refrigerator": 0.15, "oven": 0.12,
    "sink": 0.10, "toilet": 0.10, "vase": 0.04, "cup": 0.03,
    "bottle": 0.04, "bowl": 0.05, "knife": 0.02, "potted plant": 0.08,
    "backpack": 0.10, "suitcase": 0.12, "bicycle": 0.15, "dog": 0.10,
    "cat": 0.08, "cell phone": 0.03, "remote": 0.03, "mouse": 0.03,
    "keyboard": 0.06, "clock": 0.05, "mirror": 0.12,
}

class ObstacleDetector:
    def __init__(self):
        self.model = get_model()

    def detect(self, image_path: str) -> list[dict]:
        results = self.model(image_path, verbose=False)
        obstacles = []

        for r in results:
            for box in r.boxes:
                cls_name = r.names[int(box.cls)]
                conf = float(box.conf)
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]

                # position horizontale (gauche / centre / droite)
                img_width = r.orig_shape[1]
                cx = (x1 + x2) / 2
                if cx < img_width / 3:
                    position = "gauche"
                elif cx < 2 * img_width / 3:
                    position = "centre"
                else:
                    position = "droite"

                # distance normalisée par classe
                bbox_area = (x2 - x1) * (y2 - y1)
                img_area = r.orig_shape[0] * r.orig_shape[1]
                ratio = bbox_area / img_area
                ref = TAILLE_REF.get(cls_name, 0.08)
                ratio_normalise = ratio / ref

                if ratio_normalise > 2.0:
                    distance = "très proche"
                elif ratio_normalise > 0.8:
                    distance = "proche"
                else:
                    distance = "loin"

                if conf >= 0.4:
                    obstacles.append({
                        "objet": cls_name,
                        "confiance": round(conf, 2),
                        "position": position,
                        "distance": distance,
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2
                    })

        return obstacles