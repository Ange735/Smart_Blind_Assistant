# cv/finder.py
from cv.core.model_loader import get_model

def find_object(image_path: str, target: str) -> dict | None:
    model = get_model()
    results = model(image_path, verbose=False)

    best = None
    best_conf = 0.0

    for r in results:
        for box in r.boxes:
            cls_name = r.names[int(box.cls)]
            conf = float(box.conf)

            if target.lower() not in cls_name.lower():
                continue

            if conf < 0.4:
                continue

            if conf > best_conf:
                best_conf = conf
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]

                img_width = r.orig_shape[1]
                cx = (x1 + x2) / 2
                if cx < img_width / 3:
                    position = "gauche"
                elif cx < 2 * img_width / 3:
                    position = "centre"
                else:
                    position = "droite"

                best = {
                    "objet": cls_name,
                    "confiance": round(conf, 2),
                    "position": position,
                    "x1": x1, "y1": y1, "x2": x2, "y2": y2
                }

    return best  # None si pas trouvé