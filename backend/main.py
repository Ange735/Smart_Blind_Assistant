from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import shutil
import os

from cv.detector import ObstacleDetector
from cv.finder import find_object
from cv.localizer import localize

app = FastAPI()

detector = ObstacleDetector()

TEMP_IMAGE = "temp/image.jpg"
os.makedirs("temp", exist_ok=True)


def save_image(file: UploadFile) -> str:
    with open(TEMP_IMAGE, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return TEMP_IMAGE


# ================================
# ROUTE 0 : Page d'accueil
# ================================
@app.get("/")
def home():
    return {"status": "ok", "message": "API Smart Blind Assistant running"}


# ================================
# ROUTE 1 : Détecter les obstacles
# ================================
@app.post("/detect-obstacle")
async def detect_obstacle(image: UploadFile = File(...)):
    path = save_image(image)
    obstacles = detector.detect(path)
    return {"status": "ok", "obstacles": obstacles}


# ================================
# ROUTE 2 : Trouver un objet
# ================================
@app.post("/find-object")
async def find_object_route(target: str, image: UploadFile = File(...)):
    path = save_image(image)
    result = find_object(path, target)
    if result:
        return {"status": "ok", "found": True, "result": result}
    return {"status": "ok", "found": False, "message": f"'{target}' non trouvé"}


# ================================
# ROUTE 3 : Localisation utilisateur
# ================================
@app.post("/where-am-i")
async def where_am_i(image: UploadFile = File(...)):
    path = save_image(image)
    result = localize(path)
    return {"status": "ok", "result": result}


# ================================
# ROUTE 4 : Navigation
# ================================
@app.post("/navigate")
async def navigate():
    return {"status": "ok", "result": "mock", "feature": "navigate"}


# ================================
# ROUTE 5 : SOS
# ================================
@app.post("/sos")
async def sos():
    return {"status": "ok", "result": "mock", "feature": "sos"}