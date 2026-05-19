_model = None

def get_embed_model():
    """Return the shared SentenceTransformer instance, loading it only once."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model
