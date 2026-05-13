from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import shutil, os

from cv.detector  import ObstacleDetector
from cv.finder    import find_object
from cv.localizer import localize
from nlp.intent   import detect_intent

app = FastAPI()
detector = ObstacleDetector()

TEMP_IMAGE = "temp/image.jpg"
os.makedirs("temp", exist_ok=True)


# ================================
# UTILITAIRES
# ================================

def save_image(file: UploadFile) -> str:
    with open(TEMP_IMAGE, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return TEMP_IMAGE

def guide_message(target: str, position: str, distance: str) -> str:
    msg = ""
    if position == "gauche":
        msg += "Tournez légèrement à gauche. "
    elif position == "droite":
        msg += "Tournez légèrement à droite. "
    else:
        msg += "C'est droit devant. "

    if distance == "très proche":
        msg += "Vous y êtes, tendez la main."
    elif distance == "proche":
        msg += "Avancez doucement."
    else:
        msg += "Continuez d'avancer."
    return msg


# ================================
# ROUTE 0 : Page d'accueil
# ================================

@app.get("/")
def home():
    return {"status": "ok", "message": "Smart Blind Assistant API running"}


# ================================
# ROUTE 1 : Détection d'intention (NLP)
# Flutter envoie le texte reconnu par STT
# Retourne intent + entité + message vocal
# ================================

@app.post("/detect-intent")
async def route_detect_intent(phrase: str):
    result = detect_intent(phrase)
    intent = result["intent"]
    entity = result["entity"]

    messages = {
        "FIND_OBJECT": f"Je vais chercher {entity.get('value', 'l objet')}. Dirigez la caméra devant vous.",
        "LOCATE_ROOM": "Je regarde autour de vous.",
        "SOS":         "Appel des secours en cours.",
        "NAVIGATE":    "Navigation en cours de développement.",
        "UNKNOWN":     "Je n'ai pas compris. Pouvez-vous répéter ?",
    }

    return {
        "status":      "ok",
        "intent":      intent,
        "entity":      entity,
        "confident":   result["confident"],
        "tts_message": messages.get(intent, "Je n'ai pas compris.")
    }


# ================================
# ROUTE 2 : Recherche d'objet
# Flutter envoie une frame + le nom de l'objet cible
# Appelée en boucle jusqu'à ce que reached == true
# Retourne position, distance et message vocal de guidage
# ================================

@app.post("/find-object")
async def route_find_object(target: str, image: UploadFile = File(...)):
    path   = save_image(image)
    result = find_object(path, target)

    if result is None:
        return {
            "status":      "ok",
            "found":       False,
            "tts_message": "Je ne vois pas encore l'objet. Tournez légèrement."
        }

    message = guide_message(target, result["position"], result["distance"])

    return {
        "status":      "ok",
        "found":       True,
        "position":    result["position"],
        "distance":    result["distance"],
        "tts_message": message,
        "reached":     result["distance"] == "très proche"
    }


# ================================
# ROUTE 3 : Localisation utilisateur
# Flutter envoie une frame caméra
# Retourne la pièce détectée et message vocal
# ================================

@app.post("/where-am-i")
async def route_where_am_i(image: UploadFile = File(...)):
    path   = save_image(image)
    result = localize(path)
    room   = result.get("piece", "inconnue")

    if room == "inconnue":
        tts = "Je ne reconnais pas cette pièce."
    else:
        tts = f"Vous êtes dans la {room}."

    return {"status": "ok", "piece": room, "tts_message": tts}


# ================================
# ROUTE 4 : Détection d'obstacles
# Flutter envoie une frame en continu (toutes les X secondes)
# Retourne les obstacles détectés et un message vocal si danger immédiat
# ================================

@app.post("/detect-obstacle")
async def route_detect_obstacle(image: UploadFile = File(...)):
    path      = save_image(image)
    obstacles = detector.detect(path)

    tts = None
    for obs in obstacles:
        if obs["distance"] == "très proche" and obs["position"] == "centre":
            tts = f"Attention, {obs['objet']} droit devant !"
            break

    return {"status": "ok", "obstacles": obstacles, "tts_message": tts}


# ================================
# ROUTE 5 : Navigation
# ================================

@app.post("/navigate")
async def route_navigate():
    return {
        "status":      "ok",
        "tts_message": "Navigation en cours de développement.",
        "feature":     "navigate"
    }


# ================================
# ROUTE 6 : SOS
# ================================

@app.post("/sos")
async def route_sos():
    return {
        "status":      "ok",
        "tts_message": "Appel des secours en cours.",
        "feature":     "sos"
    }