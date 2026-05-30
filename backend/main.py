from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Body, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import shutil, os, uuid, asyncio, re, json
import cv2
import numpy as np

from cv.detector  import ObstacleDetector
from cv.finder    import find_object
from cv.localizer import localize
from nlp.intent   import detect_intent
from navigation.instructions import generate_instructions
from safety.sos  import declencher_sos

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = ObstacleDetector()

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
HOUSES_DIR = os.path.join(BASE_DIR, "navigation", "houses")

os.makedirs("temp",     exist_ok=True)
os.makedirs("static",   exist_ok=True)
os.makedirs(HOUSES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

BASE_URL = "http://127.0.0.1:8000"

# 🆕 Sessions actives par device_id
# Structure : { "device_id": { "active": bool, "intent": str, "target": str } }
active_sessions: dict[str, dict] = {}


# ================================
# UTILITAIRES
# ================================

def save_image(file: UploadFile) -> str:
    path = f"temp/{uuid.uuid4().hex}.jpg"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return path

def email_to_id(email: str) -> str:
    return re.sub(r'[^\w]', '_', email.lower())

async def _supprimer_apres(path: str, delai: int = 30):
    await asyncio.sleep(delai)
    if os.path.exists(path):
        os.remove(path)

def _url_vers_path(url: str) -> str:
    return url.replace(f"{BASE_URL}/static/", "static/")

def sauvegarder_image(image) -> str:
    filename = f"{uuid.uuid4().hex}.jpg"
    out_path = f"static/{filename}"
    cv2.imwrite(out_path, image)
    return f"{BASE_URL}/static/{filename}"

def annoter_finder(image_path: str, details: dict, tts_message: str = "") -> str:
    image = cv2.imread(image_path)
    if tts_message:
        cv2.putText(image, tts_message, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    if details:
        x1, y1, x2, y2 = details["x1"], details["y1"], details["x2"], details["y2"]
        label = f'{details["objet"]} | {details["distance"]} | {details["position"]}'
        cv2.rectangle(image, (x1, y1), (x2, y2), (255, 140, 0), 2)
        cv2.putText(image, label, (x1, max(y1 - 10, 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 140, 0), 2)
    return sauvegarder_image(image)

def annoter_localizer(image_path: str, piece: str, confiance: int, tts_message: str = "") -> str:
    image = cv2.imread(image_path)
    if tts_message:
        cv2.putText(image, tts_message, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    label = f"Piece : {piece} ({confiance}%)"
    cv2.putText(image, label, (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    return sauvegarder_image(image)

def annoter_detector(image_path: str, obstacles: list, tts_message: str = "") -> str:
    image = cv2.imread(image_path)
    if tts_message:
        cv2.putText(image, tts_message[:80], (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
    for obs in obstacles:
        x1, y1, x2, y2 = obs["x1"], obs["y1"], obs["x2"], obs["y2"]
        if obs["distance"] == "tres proche":
            couleur = (0, 0, 255)
        elif obs["distance"] == "proche":
            couleur = (0, 140, 255)
        else:
            couleur = (0, 255, 0)
        label = f'{obs["objet_fr"]} | {obs["distance"]} | {obs["position"]}'
        cv2.rectangle(image, (x1, y1), (x2, y2), couleur, 2)
        cv2.putText(image, label, (x1, max(y1 - 10, 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, couleur, 2)
    return sauvegarder_image(image)

class PhraseRequest(BaseModel):
    phrase: str

class SOSRequest(BaseModel):
    user_id:             str | None  = None
    message_utilisateur: str | None  = None
    localisation:        dict | None = None


# ================================
# ROUTE 0 : Page d'accueil
# ================================

@app.get("/")
def home():
    return {"status": "ok", "message": "Smart Blind Assistant API running"}


# ================================
# ROUTE 1 : Détection d'intention (NLP)
# ================================

@app.post("/detect-intent")
async def route_detect_intent(body: PhraseRequest):
    try:
        result = detect_intent(body.phrase)
        intent = result["intent"]
        entity = result["entity"]
        objet  = entity["value"] if entity and "value" in entity else "l'objet"

        messages = {
            "FIND_OBJECT": f"Je vais chercher {objet}. Dirigez la camera devant vous.",
            "LOCATE_ROOM": "Je regarde autour de vous.",
            "SOS":         "Appel des secours en cours.",
            "NAVIGATE":    "Navigation en cours.",
            "UNKNOWN":     "Je n'ai pas compris. Pouvez-vous repeter ?",
        }

        return {
            "status":           "ok",
            "intent":           intent,
            "entity":           entity,
            "confident":        result["confident"],
            "source":           result["source"],
            "phrase_originale": result["phrase_originale"],
            "phrase_nettoyee":  result["phrase_nettoyee"],
            "tts_message":      messages.get(intent, "Je n'ai pas compris.")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur NLP : {str(e)}")


# ================================
# ROUTE 2 : Recherche d'objet
# ================================

@app.post("/find-object")
async def route_find_object(
    target: str,
    image:  UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    path = None
    try:
        path      = save_image(image)
        result    = find_object(path, target)
        image_url = annoter_finder(path, result["details"], result["tts_message"])
        background_tasks.add_task(_supprimer_apres, _url_vers_path(image_url), 30)

        return {
            "status":      "ok",
            "found":       result["found"],
            "tts_message": result["tts_message"],
            "reached":     result["reached"],
            "details":     result["details"],
            "image_url":   image_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur find-object : {str(e)}")
    finally:
        if path and os.path.exists(path):
            os.remove(path)


# ================================
# ROUTE 3 : Localisation utilisateur
# ================================

@app.post("/where-am-i")
async def route_where_am_i(
    image: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    path = None
    try:
        path      = save_image(image)
        result    = localize(path)
        image_url = annoter_localizer(
            path, result["piece"], result["confiance_pct"], result["tts_message"]
        )
        background_tasks.add_task(_supprimer_apres, _url_vers_path(image_url), 30)

        return {
            "status":          "ok",
            "piece":           result["piece"],
            "confiance_pct":   result["confiance_pct"],
            "objets_detectes": result["objets_detectes"],
            "tts_message":     result["tts_message"],
            "image_url":       image_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur where-am-i : {str(e)}")
    finally:
        if path and os.path.exists(path):
            os.remove(path)


# ================================
# ROUTE 4 : Détection d'obstacles
# ================================

@app.post("/detect-obstacle")
async def route_detect_obstacle(
    image: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    path = None
    try:
        path      = save_image(image)
        result    = detector.detect(path)
        image_url = annoter_detector(path, result["obstacles"], result["tts_message"] or "")
        background_tasks.add_task(_supprimer_apres, _url_vers_path(image_url), 30)

        priorite  = 1
        interrupt = False

        if result["alertes"]:
            priorite = max(a["priorite"] for a in result["alertes"])

        if priorite >= 4:
            interrupt = True

        return {
            "status":      "ok",
            "obstacles":   result["obstacles"],
            "alertes":     result["alertes"],
            "tts_message": result["tts_message"],
            "priorite":    priorite,
            "interrupt":   interrupt,
            "image_url":   image_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur detect-obstacle : {str(e)}")
    finally:
        if path and os.path.exists(path):
            os.remove(path)


# ================================
# ROUTE 5 : Navigation
# ================================

@app.post("/navigate")
async def route_navigate(
    image:     UploadFile   = File(...),
    room_to:   str          = Form(...),
    device_id: str          = Form(default="default"),
    heading:   float | None = Form(default=None),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    path = None
    try:
        path      = save_image(image)
        loc       = localize(path)
        room_from = loc["piece"]
        confiance = loc["confiance_pct"]

        if room_from == "inconnue":
            return {
                "status":            "ok",
                "found":             False,
                "position_actuelle": "inconnue",
                "confiance_pct":     0,
                "chemin":            [],
                "instructions":      [],
                "tts_message":       "Je ne reconnais pas la piece actuelle. Orientez la camera vers des objets de la piece."
            }

        if room_from == room_to:
            return {
                "status":            "ok",
                "found":             True,
                "position_actuelle": room_from,
                "confiance_pct":     confiance,
                "chemin":            [room_from],
                "instructions":      [f"Vous etes deja dans la {room_to}."],
                "tts_message":       f"Vous etes deja dans la {room_to}."
            }

        result = generate_instructions(room_from, room_to, device_id, heading)

        return {
            "status":            "ok",
            "device_id":         device_id,
            "heading":           heading,
            "position_actuelle": room_from,
            "confiance_pct":     confiance,
            "found":             result["found"],
            "chemin":            result["chemin"],
            "instructions":      result["instructions"],
            "tts_message":       result["tts_message"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur navigate : {str(e)}")
    finally:
        if path and os.path.exists(path):
            os.remove(path)


# ================================
# ROUTE 6 : SOS
# ================================

@app.post("/sos")
async def route_sos(payload: SOSRequest = SOSRequest()):
    try:
        result = declencher_sos(
            user_id=payload.user_id,
            message_utilisateur=payload.message_utilisateur,
            localisation=payload.localisation,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur SOS : {str(e)}")


# ================================
# ROUTE 7 : Sauvegarder la config maison
# ================================

@app.post("/house/save")
async def route_save_house(device_id: str, house: dict = Body(...)):
    try:
        safe_name = email_to_id(device_id)
        filepath  = os.path.join(HOUSES_DIR, f"house_{safe_name}.json")

        if os.path.exists(filepath):
            return {
                "status":  "error",
                "message": f"Une configuration existe deja pour {device_id}. Utilisez /house/update.",
                "device_id": device_id
            }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(house, f, ensure_ascii=False, indent=4)

        return {
            "status":    "ok",
            "message":   "Maison sauvegardee avec succes.",
            "device_id": device_id,
            "fichier":   f"house_{safe_name}.json"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur house/save : {str(e)}")


# ================================
# ROUTE 8 : Récupérer la config maison
# ================================

@app.get("/house")
async def route_get_house(device_id: str = "default"):
    try:
        if device_id == "default":
            filepath = os.path.join(BASE_DIR, "navigation", "house_default.json")
        else:
            safe_name = email_to_id(device_id)
            filepath  = os.path.join(HOUSES_DIR, f"house_{safe_name}.json")

        if not os.path.exists(filepath):
            filepath = os.path.join(BASE_DIR, "navigation", "house_default.json")

        if not os.path.exists(filepath):
            raise FileNotFoundError("Aucune configuration maison trouvee.")

        with open(filepath, "r", encoding="utf-8") as f:
            house = json.load(f)

        return {"status": "ok", "device_id": device_id, "house": house}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur house/get : {str(e)}")


# ================================
# ROUTE 9 : Mettre à jour la config maison
# ================================

@app.put("/house/update")
async def route_update_house(device_id: str, house: dict = Body(...)):
    try:
        safe_name = email_to_id(device_id)
        filepath  = os.path.join(HOUSES_DIR, f"house_{safe_name}.json")

        if not os.path.exists(filepath):
            raise HTTPException(
                status_code=404,
                detail=f"Aucune configuration trouvee pour {device_id}. Utilisez /house/save d'abord."
            )

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(house, f, ensure_ascii=False, indent=4)

        return {
            "status":    "ok",
            "message":   "Configuration mise a jour avec succes.",
            "device_id": device_id,
            "fichier":   f"house_{safe_name}.json"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur house/update : {str(e)}")


# ================================
# 🆕 ROUTE 10 : Annuler une action en cours
# ================================

@app.post("/cancel")
async def route_cancel(device_id: str = Form(default="default")):
    session = active_sessions.get(device_id)
    if session and session.get("active"):
        active_sessions[device_id]["active"] = False
        intent = session.get("intent", "")
        messages = {
            "FIND_OBJECT": "Recherche annulée.",
            "NAVIGATE":    "Navigation annulée.",
        }
        tts = messages.get(intent, "Action annulée.")
        return {"status": "ok", "cancelled": True, "tts_message": tts}
    return {"status": "ok", "cancelled": False, "tts_message": "Aucune action en cours."}


# ================================
# ROUTE PIPELINE
# ================================

@app.post("/pipeline")
async def route_pipeline(
    phrase:    str          = Form(...),
    image:     UploadFile   = File(...),
    device_id: str          = Form(default="default"),
    heading:   float | None = Form(default=None),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    path = None
    image_url = None

    action = {
        "loop":           False,
        "loop_interval":  0,
        "stop_obstacle":  False,
        "vibration":      "none",
        "show_emergency": False,
        "mode":           "normal"
    }

    try:
        path = save_image(image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impossible de sauvegarder l'image : {str(e)}")

    # ── Étape 1 : NLP ─────────────────────────────────────────────────
    try:
        nlp_result = detect_intent(phrase)
    except Exception as e:
        if path and os.path.exists(path):
            os.remove(path)
        raise HTTPException(status_code=500, detail=f"Erreur NLP pipeline : {str(e)}")

    intent     = nlp_result["intent"]
    entity     = nlp_result["entity"]
    objet      = entity.get("value", "") if entity else ""
    yolo_class = entity.get("yolo_class", objet) if entity else objet

    # 🆕 Vérifie si l'utilisateur veut annuler ("stop", "annuler", "arrêter")
    CANCEL_KEYWORDS = {"stop", "annuler", "arrête", "arreter", "stopper", "quitter", "terminer"}
    phrase_lower = phrase.lower().strip()
    if any(kw in phrase_lower for kw in CANCEL_KEYWORDS):
        session = active_sessions.get(device_id)
        if session and session.get("active"):
            active_sessions[device_id]["active"] = False
            intent_annule = session.get("intent", "")
            messages_annule = {
                "FIND_OBJECT": f"Recherche de {session.get('target', 'l objet')} annulée.",
                "NAVIGATE":    "Navigation annulée.",
            }
            tts_annule = messages_annule.get(intent_annule, "Action annulée.")
            if path and os.path.exists(path):
                os.remove(path)
            return {
                "status":           "ok",
                "phrase_originale": phrase,
                "phrase_nettoyee":  phrase,
                "intent":           "CANCEL",
                "source":           "cancel_keywords",
                "entity":           None,
                "confident":        True,
                "device_id":        device_id,
                "heading":          heading,
                "cv_result":        {"tts_message": tts_annule},
                "tts_message":      tts_annule,
                "action": {
                    "loop":           False,
                    "loop_interval":  0,
                    "stop_obstacle":  False,
                    "vibration":      "none",
                    "show_emergency": False,
                    "mode":           "normal"  # 🆕 repasse en normal → Flutter stop le loop
                },
                "image_url": None
            }

    cv_result = {}

    # ── Étape 2 : Routage ──────────────────────────────────────────────
    try:

        # ── FIND_OBJECT ───────────────────────────────────────────────
        if intent == "FIND_OBJECT":
            if not objet:
                cv_result = {"tts_message": "Quel objet cherchez-vous ?"}
                image_url = sauvegarder_image(cv2.imread(path))

            elif entity and not entity.get("detectable", False):
                cv_result = {
                    "tts_message": f"Je ne peux pas detecter {objet} visuellement."
                }
                image_url = sauvegarder_image(cv2.imread(path))

            else:
                # 🆕 Vérifie si la session est toujours active avant de traiter
                session = active_sessions.get(device_id, {})
                if not session.get("active", True) and session.get("intent") == "FIND_OBJECT":
                    if path and os.path.exists(path):
                        os.remove(path)
                    return {
                        "status": "ok", "tts_message": "Recherche annulée.",
                        "action": {**action, "mode": "normal"}, "image_url": None,
                        "cv_result": {"tts_message": "Recherche annulée."},
                        "intent": "CANCEL", "device_id": device_id,
                        "phrase_originale": phrase, "phrase_nettoyee": phrase,
                        "source": "", "entity": entity, "confident": False, "heading": heading
                    }

                target    = yolo_class or objet
                result    = find_object(path, target)
                image_url = annoter_finder(path, result["details"], result["tts_message"])
                cv_result = {
                    "found":       result["found"],
                    "reached":     result["reached"],
                    "details":     result["details"],
                    "tts_message": result["tts_message"]
                }
                if not result["reached"]:
                    # 🆕 Enregistre la session active
                    active_sessions[device_id] = {
                        "active": True,
                        "intent": "FIND_OBJECT",
                        "target": target
                    }
                    action["loop"]          = True
                    action["loop_interval"] = 5
                    action["stop_obstacle"] = True
                    action["mode"]          = "find_object"
                else:
                    # 🆕 Objet atteint → ferme la session automatiquement
                    active_sessions[device_id] = {"active": False, "intent": "", "target": ""}
                    action["mode"] = "normal"

        # ── LOCATE_ROOM ───────────────────────────────────────────────
        elif intent == "LOCATE_ROOM":
            result    = localize(path)
            image_url = annoter_localizer(
                path, result["piece"], result["confiance_pct"], result["tts_message"]
            )
            cv_result = {
                "piece":           result["piece"],
                "confiance_pct":   result["confiance_pct"],
                "objets_detectes": result["objets_detectes"],
                "tts_message":     result["tts_message"]
            }
            action["mode"] = "normal"

        # ── NAVIGATE ──────────────────────────────────────────────────
        elif intent == "NAVIGATE":
            room_to = objet if objet else None

            if not room_to:
                cv_result = {"tts_message": "Ou voulez-vous aller ?"}
                image_url = sauvegarder_image(cv2.imread(path))
            else:
                loc       = localize(path)
                room_from = loc["piece"]
                confiance = loc["confiance_pct"]

                if room_from == "inconnue":
                    cv_result = {
                        "tts_message": "Je ne reconnais pas la piece actuelle. Orientez la camera."
                    }
                    image_url = annoter_localizer(path, "inconnue", 0, cv_result["tts_message"])
                else:
                    nav_result = generate_instructions(room_from, room_to, device_id, heading)
                    image_url  = annoter_localizer(
                        path, room_from, confiance, nav_result["tts_message"]
                    )
                    cv_result = {
                        "position_actuelle": room_from,
                        "confiance_pct":     confiance,
                        "destination":       room_to,
                        "found":             nav_result["found"],
                        "chemin":            nav_result["chemin"],
                        "instructions":      nav_result["instructions"],
                        "tts_message":       nav_result["tts_message"]
                    }
                    arrived = (len(nav_result["chemin"]) <= 1 or room_from == room_to)
                    if not arrived:
                        # 🆕 Enregistre la session active
                        active_sessions[device_id] = {
                            "active": True,
                            "intent": "NAVIGATE",
                            "target": room_to
                        }
                        action["loop"]          = True
                        action["loop_interval"] = 5
                        action["stop_obstacle"] = True
                        action["mode"]          = "navigate"
                    else:
                        # 🆕 Arrivée → ferme la session automatiquement
                        active_sessions[device_id] = {"active": False, "intent": "", "target": ""}
                        action["mode"] = "normal"

        # ── SOS ───────────────────────────────────────────────────────
        elif intent == "SOS":
            sos_result = declencher_sos(
                user_id=device_id,
                message_utilisateur=phrase,
                localisation=None
            )
            cv_result = {
                "tts_message": sos_result["message_retour"],
            }
            image_url                = sauvegarder_image(cv2.imread(path))
            action["vibration"]      = "strong"
            action["show_emergency"] = True
            action["stop_obstacle"]  = True
            action["mode"]           = "sos"

        # ── UNKNOWN → détection obstacles ─────────────────────────────
        else:
            result    = detector.detect(path)
            image_url = annoter_detector(path, result["obstacles"], result["tts_message"] or "")
            cv_result = {
                "obstacles":   result["obstacles"],
                "alertes":     result["alertes"],
                "tts_message": result["tts_message"] or "Je n'ai pas compris. Voici ce que je detecte."
            }
            action["mode"] = "normal"

    except Exception as e:
        cv_result = {
            "tts_message": "Une erreur interne s'est produite. Veuillez reessayer."
        }
        action["mode"] = "normal"
        try:
            raw = cv2.imread(path)
            if raw is not None:
                image_url = sauvegarder_image(raw)
        except Exception:
            image_url = None
        print(f"[PIPELINE ERROR] intent={intent} | error={str(e)}")

    finally:
        if path and os.path.exists(path):
            os.remove(path)
        if image_url:
            background_tasks.add_task(_supprimer_apres, _url_vers_path(image_url), 30)

    return {
        "status":           "ok",
        "phrase_originale": nlp_result.get("phrase_originale", phrase),
        "phrase_nettoyee":  nlp_result.get("phrase_nettoyee", phrase),
        "intent":           intent,
        "source":           nlp_result.get("source", ""),
        "entity":           entity,
        "confident":        nlp_result.get("confident", False),
        "device_id":        device_id,
        "heading":          heading,
        "cv_result":        cv_result,
        "tts_message":      cv_result.get("tts_message", ""),
        "action":           action,
        "image_url":        image_url
    }