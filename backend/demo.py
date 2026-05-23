from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Form
from fastapi.staticfiles import StaticFiles
import shutil, os, uuid, asyncio
import cv2

from cv.detector             import ObstacleDetector
from cv.finder               import find_object
from cv.localizer            import localize
from nlp.intent              import detect_intent
from safety.sos              import declencher_sos
from navigation.instructions import generate_instructions

app = FastAPI()
detector = ObstacleDetector()

os.makedirs("temp", exist_ok=True)
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

BASE_URL = "http://127.0.0.1:8001"


# ================================
# UTILITAIRES
# ================================

def save_image(file: UploadFile) -> str:
    path = f"temp/{uuid.uuid4().hex}.jpg"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return path

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


# ================================
# ROUTE 0 : Page d'accueil
# ================================

@app.get("/")
def home():
    return {"status": "ok", "message": "Smart Blind Assistant — Demo Pipeline"}


# ================================
# ROUTE PRINCIPALE : Pipeline complet
# 1. NLP  — détection d'intention + entité
# 2. CV   — appel automatique du bon module
# 3. Retourne résultat + image annotée
# ================================

@app.post("/pipeline")
async def route_pipeline(
    phrase:    str            = Form(...),
    image:     UploadFile     = File(...),
    room_from: str            = Form(default=""),   # ← pièce de départ (navigation)
    room_to:   str            = Form(default=""),   # ← pièce cible    (navigation)
    device_id: str            = Form(default="default"),
    heading:   float | None   = Form(default=None), # ← compass Flutter (optionnel)
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    path = save_image(image)

    # ── Étape 1 : NLP ────────────────────────────────────────────────────
    nlp_result = detect_intent(phrase)
    intent     = nlp_result["intent"]
    entity     = nlp_result["entity"]
    objet      = entity.get("value", "") if entity else ""

    # ── Étape 2 : Routage ─────────────────────────────────────────────────
    cv_result = {}
    image_url = None

    if intent == "FIND_OBJECT":
        if not objet:
            cv_result = {"tts_message": "Quel objet cherchez-vous ?"}
            image_url = sauvegarder_image(cv2.imread(path))
        else:
            result    = find_object(path, objet)
            image_url = annoter_finder(path, result["details"], result["tts_message"])
            cv_result = {
                "found":       result["found"],
                "reached":     result["reached"],
                "details":     result["details"],
                "tts_message": result["tts_message"]
            }

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

    elif intent == "SOS":
        sos_result = declencher_sos(
            user_id=None,
            message_utilisateur=phrase,
            localisation=None
        )
        image_url = sauvegarder_image(cv2.imread(path))
        cv_result = {
            "tts_message":            sos_result["message_retour"],
            "vibration":              sos_result["vibration"],
            "son_alarme":             sos_result["son_alarme"],
            "afficher_ecran_urgence": sos_result["afficher_ecran_urgence"],
            "timestamp":              sos_result["timestamp"],
        }

    elif intent == "NAVIGATE":
        # ── Navigation : room_from et room_to extraits de l'entité ou du Form ──
        rf = room_from.strip()
        rt = room_to.strip()

        # Fallback : si le NLP a extrait une destination dans l'entité
        if not rt and entity and "value" in entity:
            rt = entity["value"]

        if not rf or not rt:
            cv_result = {
                "tts_message": "Précisez la pièce de départ et la destination.",
                "found":       False,
                "chemin":      [],
                "instructions": []
            }
        else:
            nav_result = generate_instructions(rf, rt, device_id, heading)
            cv_result  = {
                "tts_message":  nav_result["tts_message"],
                "found":        nav_result["found"],
                "chemin":       nav_result["chemin"],
                "instructions": nav_result["instructions"],
            }

        image_url = sauvegarder_image(cv2.imread(path))

    else:  # UNKNOWN → détection d'obstacles par défaut
        result    = detector.detect(path)
        image_url = annoter_detector(path, result["obstacles"], result["tts_message"] or "")
        cv_result = {
            "obstacles":   result["obstacles"],
            "alertes":     result["alertes"],
            "tts_message": result["tts_message"] or "Je n'ai pas compris. Analyse de la scene effectuee."
        }

    os.remove(path)
    background_tasks.add_task(_supprimer_apres, _url_vers_path(image_url), 30)

    # ── Étape 3 : Réponse complète ────────────────────────────────────────
    return {
        "status":    "ok",
        "phrase":    phrase,
        "intent":    intent,
        "entity":    entity,
        "confident": nlp_result["confident"],
        "cv_result": cv_result,
        "image_url": image_url
    }