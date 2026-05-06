import sys
sys.path.append(".")

import cv2
from cv.detector import ObstacleDetector

detector = ObstacleDetector()
image_path = "image_test/4.png"
results = detector.detect(image_path)

# charger l'image
image = cv2.imread(image_path)

for obj in results:
    print(obj)

    x1, y1, x2, y2 = int(obj["x1"]), int(obj["y1"]), int(obj["x2"]), int(obj["y2"])
    label = f'{obj["objet"]} | {obj["distance"]} | {obj["position"]} ({obj["confiance"]})'

    # rectangle
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    # texte
    cv2.putText(image, label, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

cv2.imshow("Détection", image)
cv2.waitKey(0)
cv2.destroyAllWindows()