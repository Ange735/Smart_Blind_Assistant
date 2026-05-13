# cv/core/depth_loader.py
from transformers import pipeline

_depth_pipe = None

def get_depth_model():
    global _depth_pipe
    if _depth_pipe is None:
        print("[DepthLoader] Chargement Depth Anything V2...")
        _depth_pipe = pipeline(
            task="depth-estimation",
            model="depth-anything/Depth-Anything-V2-Small-hf"
        )
        print("[DepthLoader] Modèle profondeur prêt ✅")
    return _depth_pipe