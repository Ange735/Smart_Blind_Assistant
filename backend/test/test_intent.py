import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from nlp.intent import detect_intent

phrases_test = [
    # Intent + entité objet
    ("trouve mes lunettes",         "FIND_OBJECT"),
    ("je cherche mon téléphone",    "FIND_OBJECT"),
    ("où est mon portefeuille",     "FIND_OBJECT"),
    ("tu vois mes clés",            "FIND_OBJECT"),

    # Intent + entité pièce
    ("va à la cuisine",             "NAVIGATE"),
    ("amène-moi au salon",          "NAVIGATE"),
    ("guide-moi vers la chambre",   "NAVIGATE"),

    # Sans entité
    ("où suis-je",                  "LOCATE_ROOM"),
    ("au secours",                  "SOS"),

    # UNKNOWN
    ("bonjour",                     "UNKNOWN"),
    ("merci",                       "UNKNOWN"),
    ("ok d'accord",                 "UNKNOWN"),
    ("je ne sais pas",              "UNKNOWN"),
    
    #test entités canonisées
    ("tu vois ma clef",             "FIND_OBJECT"),
    ("je cherche mes chaussure",    "FIND_OBJECT"),
    ("va à la salle de bains",      "NAVIGATE"),
    ("amène-moi au living",         "NAVIGATE"),
    ("je ne vois pas ma télécommande", "FIND_OBJECT"),
]

for phrase, expected in phrases_test:
    result = detect_intent(phrase)
    status = "✅" if result["intent"] == expected else "❌"
    print(f"{status} '{phrase}' → {result['intent']} (score={result['score']}, margin={result['margin']}) | entité: {result['entity']}")