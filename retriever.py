from db import get_collection
from embedder import get_embed_model

def retrieve(query, top_k=10):
    embed_model = get_embed_model()
    query_embedding = embed_model.encode([query]).tolist()
    collection = get_collection()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    chunks = results["documents"][0]
    metas = results["metadatas"][0]
    return list(zip(chunks, metas))