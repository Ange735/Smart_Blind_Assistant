import sys
sys.path.append(".")

import cv2
from cv.finder import find_object

image_path = "image_test/1.png"
result = find_object(image_path, "bottle")

image = cv2.imread(image_path)

if result:
    print(f"Trouvé : {result}")
    x1, y1, x2, y2 = result["x1"], result["y1"], result["x2"], result["y2"]
    label = f'{result["objet"]} | {result["position"]} ({result["confiance"]})'
    cv2.rectangle(image, (x1, y1), (x2, y2), (255, 140, 0), 2)
    cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 140, 0), 2)
else:
    print("Objet non trouvé.")
    cv2.putText(image, "Objet non trouve", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

cv2.imshow("Finder", image)
cv2.waitKey(0)
cv2.destroyAllWindows()