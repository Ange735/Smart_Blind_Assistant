import sys
sys.path.append(".")

import cv2
from cv.localizer import localize

image_path = "image_test/2.png"
result = localize(image_path)

print(f"Pièce détectée : {result['piece']} (score: {result['score']})")
print(f"Objets vus : {result['objets_detectes']}")

image = cv2.imread(image_path)
label = f"Piece : {result['piece']} (score: {result['score']})"
cv2.putText(image, label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 0), 2)
cv2.imshow("Localizer", image)
cv2.waitKey(0)
cv2.destroyAllWindows()