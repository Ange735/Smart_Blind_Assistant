import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import cv2
from cv.finder import find_object

image_path = os.path.join(os.path.dirname(__file__), '..', 'image_test', '5.png')
result = find_object(image_path, "bed")

image = cv2.imread(image_path)

# ── Affichage terminal ────────────────────────────────────────────────────────
print(f"Trouve      : {result['found']}")
print(f"Message TTS : {result['tts_message']}")
print(f"Atteint     : {result['reached']}")

# ── Affichage image ───────────────────────────────────────────────────────────
if result["found"] and result["details"]:
    details = result["details"]
    print(f"Details     : {details}")

    x1, y1, x2, y2 = details["x1"], details["y1"], details["x2"], details["y2"]

    label = f'{details["objet"]} | {details["distance"]} | {details["position"]} ({details["confiance"]})'

    cv2.rectangle(image, (x1, y1), (x2, y2), (255, 140, 0), 2)
    cv2.putText(image, label, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 140, 0), 2)

    # Message TTS en haut de l'image
    cv2.putText(image, result["tts_message"], (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

else:
    print(f"Details     : objet non trouve")
    cv2.putText(image, result["tts_message"], (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

cv2.imshow("Finder", image)
cv2.waitKey(0)
cv2.destroyAllWindows()