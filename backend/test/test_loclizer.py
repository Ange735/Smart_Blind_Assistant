# test/test_localizer.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import cv2
from cv.localizer import localize

image_path = os.path.join(os.path.dirname(__file__), '..', 'image_test', '5.png')
result     = localize(image_path)

# ── Affichage terminal ────────────────────────────────────────────────────────
print(f"Piece          : {result['piece']}")
print(f"Score          : {result['score']}")
print(f"Confiance      : {result['confiance_pct']}%")
print(f"Message TTS    : {result['tts_message']}")
print(f"Objets detectes: {result['objets_detectes']}")

# ── Affichage image ───────────────────────────────────────────────────────────
image = cv2.imread(image_path)

# Message TTS en haut
cv2.putText(image, result["tts_message"], (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

# Confiance
cv2.putText(image, f"Confiance : {result['confiance_pct']}%", (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

# Objets détectés en bas
objets_str = f"Objets : {', '.join(result['objets_detectes'])}"
cv2.putText(image, objets_str, (20, image.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 0), 1)

cv2.imshow("Localizer", image)
cv2.waitKey(0)
cv2.destroyAllWindows()