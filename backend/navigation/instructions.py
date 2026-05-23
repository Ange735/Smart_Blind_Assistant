# navigation/instructions.py
from navigation.pathfinder import find_path


def _calculer_direction(heading: float, angle_cible: float) -> str:
    """
    Calcule la direction relative (gauche/droite/avancez)
    selon le heading actuel de l'utilisateur et l'angle cible.

    heading     : direction où regarde l'utilisateur (0-360, 0=Nord)
    angle_cible : direction absolue vers la pièce cible (0-360)
    """
    diff = (angle_cible - heading) % 360

    if diff < 30 or diff > 330:
        return "avancez"
    elif diff <= 180:
        return "tournez a droite"
    else:
        return "tournez a gauche"


def generate_instructions(
    room_from: str,
    room_to:   str,
    device_id: str   = None,
    heading:   float = None    # ← heading du compass Flutter (optionnel)
) -> dict:
    """
    Génère les instructions vocales.
    Si heading fourni → gauche/droite calculés dynamiquement.
    Si heading absent → instructions génériques (avancez vers X).
    """
    if room_from == room_to:
        msg = f"Vous etes deja dans la {room_to}."
        return {
            "found":        True,
            "chemin":       [room_from],
            "instructions": [msg],
            "tts_message":  msg
        }

    path = find_path(room_from, room_to, device_id)

    if path is None:
        msg = f"Je ne connais pas le chemin de {room_from} vers {room_to}."
        return {
            "found":        False,
            "chemin":       [],
            "instructions": [msg],
            "tts_message":  msg
        }

    instructions = []
    chemin       = [path[0]["de"]]

    for etape in path:
        chemin.append(etape["vers"])
        vers  = etape["vers"]
        angle = etape["angle"]

        if heading is not None:
            # ── Direction calculée selon l'orientation réelle ─────────────
            direction = _calculer_direction(heading, angle)
            if direction == "avancez":
                msg = f"Avancez vers la {vers}."
            elif direction == "tournez a droite":
                msg = f"Tournez a droite vers la {vers}."
            else:
                msg = f"Tournez a gauche vers la {vers}."
        else:
            # ── Pas de heading → instruction générique ────────────────────
            msg = f"Dirigez-vous vers la {vers}."

        instructions.append(msg)

    instructions.append("Vous etes arrive !")

    return {
        "found":        True,
        "chemin":       chemin,
        "instructions": instructions,
        "tts_message":  " ".join(instructions)
    }