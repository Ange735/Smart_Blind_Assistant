"""
Module SOS — Phase 6 : Gestion des urgences vocales
"""

import logging
import datetime
from typing import Optional

logger = logging.getLogger("SOS_URGENCE")
logger.setLevel(logging.WARNING)

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    "🚨 [%(levelname)s] %(asctime)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))
logger.addHandler(handler)


def declencher_sos(
    user_id: Optional[str] = None,
    message_utilisateur: Optional[str] = None,
    localisation: Optional[dict] = None
) -> dict:

    timestamp = datetime.datetime.now().isoformat()

    # 1. LOG
    logger.warning(
        f"ALERTE SOS DÉCLENCHÉE | user_id={user_id} | "
        f"message='{message_utilisateur}' | localisation={localisation}"
    )

    # 2. PRINT CONSOLE (démo)
    print("\n" + "=" * 60)
    print("🚨🚨🚨  ALERTE SOS DÉCLENCHÉE  🚨🚨🚨")
    print(f"  Timestamp    : {timestamp}")
    print(f"  Utilisateur  : {user_id or 'inconnu'}")
    print(f"  Message      : {message_utilisateur or '(aucun)'}")
    print(f"  Localisation : {localisation or 'non fournie'}")
    print("=" * 60)
    print("📞 [SIMULATION] Appel vers numéro d'urgence 15 / 112...")
    print("📲 [SIMULATION] Notification envoyée aux contacts d'urgence")
    print("=" * 60 + "\n")

    # 3. RÉPONSE
    return {
        "status": "sos_triggered",
        "timestamp": timestamp,
        "user_id": user_id,
        "message_recu": message_utilisateur,
        "localisation": localisation,
        "vibration": "strong",
        "son_alarme": True,
        "afficher_ecran_urgence": True,
        "message_retour": "SOS reçu. Les secours ont été alertés. Restez en ligne.",
    }