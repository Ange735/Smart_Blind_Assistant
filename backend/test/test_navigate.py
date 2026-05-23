import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from navigation.instructions import generate_instructions

print("=" * 55)
print("TEST MODULE NAVIGATION")
print("=" * 55)

tests = [
    # (room_from, room_to, description)
    ("salon",         "cuisine",       "Trajet normal"),
    ("chambre",       "cuisine",       "Trajet multi-etapes"),
    ("salle_de_bain", "salon",         "Trajet inverse"),
    ("salon",         "salon",         "Deja dans la piece"),
    ("salon",         "inexistant",    "Piece inconnue"),
    ("cuisine",       "salle_de_bain", "Trajet long"),
]

for room_from, room_to, description in tests:
    result = generate_instructions(room_from, room_to)
    status = "✅" if result["found"] or room_from == room_to else "⚠️"

    print(f"\n{status} [{description}] {room_from} → {room_to}")
    print(f"   Chemin : {' → '.join(result['chemin']) if result['chemin'] else 'aucun'}")
    print(f"   TTS    : {result['tts_message']}")