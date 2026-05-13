# cv/core/model_loader.py
from ultralytics import YOLO

_model_coco = None
_model_custom = None

def get_model_coco(path="cv/models/yolov8n.pt"):
    global _model_coco
    if _model_coco is None:
        print(f"[ModelLoader] Chargement modèle COCO : {path}")
        _model_coco = YOLO(path)
        print("[ModelLoader] Modèle COCO prêt ✅")
    return _model_coco

def get_model_custom(path="cv/models/best.pt"):
    global _model_custom
    if _model_custom is None:
        print(f"[ModelLoader] Chargement modèle custom : {path}")
        _model_custom = YOLO(path)
        print("[ModelLoader] Modèle custom prêt ✅")
    return _model_custom