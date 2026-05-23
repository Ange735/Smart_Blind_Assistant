# nlp/model_loader.py
import os
import threading
from sentence_transformers import SentenceTransformer

_model      = None
_spacy_model = None
_lock       = threading.Lock()

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
CACHE_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".model_cache")


# ================================
# SENTENCE TRANSFORMER
# ================================

def get_model() -> SentenceTransformer:
    global _model
    if _model is not None:
        return _model
    with _lock:
        if _model is not None:
            return _model
        try:
            print(f"Chargement du modèle NLP ({MODEL_NAME})...")
            _model = SentenceTransformer(MODEL_NAME, cache_folder=CACHE_DIR)
            print("Modèle NLP chargé ✅")
        except Exception as e:
            raise RuntimeError(f"Impossible de charger '{MODEL_NAME}'.") from e
    return _model


# ================================
# SPACY
# ================================

def get_spacy_model():
    global _spacy_model
    if _spacy_model is not None:
        return _spacy_model
    with _lock:
        if _spacy_model is not None:
            return _spacy_model
        try:
            import spacy
            print("Chargement du modèle spaCy (fr_core_news_sm)...")
            _spacy_model = spacy.load("fr_core_news_sm")
            print("Modèle spaCy chargé ✅")
        except OSError:
            print("[NLP] spaCy non disponible — fallback désactivé")
            _spacy_model = None
    return _spacy_model


# ================================
# UTILITAIRE
# ================================

def unload_models():
    """Libère tous les modèles NLP de la mémoire."""
    global _model, _spacy_model
    with _lock:
        _model       = None
        _spacy_model = None
        print("Modèles NLP déchargés.")