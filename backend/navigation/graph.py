# navigation/graph.py
import json, os, re

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
HOUSES_DIR = os.path.join(BASE_DIR, "houses")
DEFAULT    = os.path.join(BASE_DIR, "house_default.json")

os.makedirs(HOUSES_DIR, exist_ok=True)

def email_to_id(email: str) -> str:
    return re.sub(r'[^\w]', '_', email.lower())

def _charger_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_graph(device_id: str = None) -> dict:
    if device_id and device_id != "default":
        path = os.path.join(HOUSES_DIR, f"house_{email_to_id(device_id)}.json")
        data = _charger_json(path) if os.path.exists(path) else _charger_json(DEFAULT)
    else:
        data = _charger_json(DEFAULT)

    graph = {room: [] for room in data["rooms"]}
    for conn in data["connections"]:
        graph[conn["from"]].append({
            "voisin": conn["to"],
            "angle":  conn.get("angle", 0)   # ← angle absolu
        })
    return graph