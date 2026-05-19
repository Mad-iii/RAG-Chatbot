from db import get_collection
from embedder import get_embed_model

def retrieve(query, top_k=5, max_per_source=3):
    embed_model = get_embed_model()
    query_embedding = embed_model.encode([query]).tolist()
    collection = get_collection()

    # fetch more than needed so we can diversify across sources
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k * 4, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    chunks = results["documents"][0]
    metas = results["metadatas"][0]

    # pick up to max_per_source chunks per PDF
    seen = {}
    diverse = []
    for chunk, meta in zip(chunks, metas):
        src = meta["source"]
        seen[src] = seen.get(src, 0)
        if seen[src] < max_per_source:
            diverse.append((chunk, meta))
            seen[src] += 1

    return diverse