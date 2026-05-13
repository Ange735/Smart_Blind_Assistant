import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import cv2
from cv.detector import ObstacleDetector

detector  = ObstacleDetector()
image_path = os.path.join(os.path.dirname(__file__), '..', 'image_test', '5.png')

results = detector.detect(image_path)
image   = cv2.imread(image_path)

# ── Affichage terminal ────────────────────────────────────────────────────────
print(f"TTS prioritaire : {results['tts_message']}")
print(f"Nombre alertes  : {len(results['alertes'])}")

for alerte in results["alertes"]:
    print(f"  ⚠️  [{alerte['priorite']}] {alerte['message']}")

print(f"\nNombre obstacles : {len(results['obstacles'])}")
for obs in results["obstacles"]:
    print(f"  → {obs['objet_fr']} | {obs['distance']} | {obs['position']} ({obs['confiance']})")

# ── Affichage image ───────────────────────────────────────────────────────────

# Message TTS en haut de l'image
if results["tts_message"]:
    lignes = results["tts_message"].split("\n")
    for i, ligne in enumerate(lignes):
        cv2.putText(image, ligne, (10, 30 + i * 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)

for obs in results["obstacles"]:
    x1, y1, x2, y2 = int(obs["x1"]), int(obs["y1"]), int(obs["x2"]), int(obs["y2"])

    # Couleur selon distance
    if obs["distance"] == "tres proche":
        couleur = (0, 0, 255)    # rouge
    elif obs["distance"] == "proche":
        couleur = (0, 165, 255)  # orange
    else:
        couleur = (0, 255, 0)    # vert

    label = f'{obs["objet_fr"]} | {obs["distance"]} | {obs["position"]} ({obs["confiance"]})'

    cv2.rectangle(image, (x1, y1), (x2, y2), couleur, 2)
    cv2.putText(image, label, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, couleur, 2)

cv2.imshow("Detection", image)
cv2.waitKey(0)
cv2.destroyAllWindows()