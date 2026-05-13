# model_loader.py
import os
import threading
from sentence_transformers import SentenceTransformer

_model = None
_lock = threading.Lock()  # Sécurité si plusieurs threads chargent en même temps

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# Dossier local pour éviter de re-télécharger à chaque environnement
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".model_cache")

def get_model() -> SentenceTransformer:
    global _model

    if _model is not None:
        return _model

    with _lock:
        # Double vérification : un autre thread a peut-être chargé entre-temps
        if _model is not None:
            return _model

        try:
            print(f"Chargement du modèle NLP ({MODEL_NAME})...")
            _model = SentenceTransformer(MODEL_NAME, cache_folder=CACHE_DIR)
            print("Modèle NLP chargé ✅")

        except Exception as e:
            print(f"Erreur chargement modèle : {e}")
            raise RuntimeError(
                f"Impossible de charger le modèle '{MODEL_NAME}'.\n"
                f"Vérifie ta connexion ou le cache dans {CACHE_DIR}."
            ) from e

    return _model


def unload_model():
    """Libère la mémoire si nécessaire (utile en tests ou en prod contrainte)."""
    global _model
    with _lock:
        _model = None
        print("Modèle NLP déchargé.")