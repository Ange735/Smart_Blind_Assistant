# core/model_loader.py
from ultralytics import YOLO

_model = None

def get_model(path="cv/models/yolov8n.pt"):
    global _model
    if _model is None:
        print(f"[ModelLoader] Chargement du modèle : {path}")
        _model = YOLO(path)
        print("[ModelLoader] Modèle prêt ✅")
    return _model