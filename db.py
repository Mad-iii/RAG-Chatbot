_client = None
_collection = None

def get_collection():
    """Return the shared ChromaDB collection, opening the client only once."""
    global _client, _collection
    if _client is None:
        import chromadb
        _client = chromadb.PersistentClient(path="./chroma_store")
        _collection = _client.get_or_create_collection("rag_docs")
    return _collection
