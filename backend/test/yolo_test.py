from ultralytics import YOLO

model = YOLO("yolov8n.pt")
results = model("image_test/6.png")  # mets le chemin d'une vraie image

for r in results:
    for box in r.boxes:
        cls_name = r.names[int(box.cls)]
        conf = float(box.conf)
        print(f"{cls_name} — confiance: {conf:.2f}")

results[0].show()