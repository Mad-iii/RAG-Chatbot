import chromadb
from sentence_transformers import SentenceTransformer

EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_store")
collection = client.get_or_create_collection("rag_docs")

def retrieve(query, top_k=10):
    query_embedding = EMBED_MODEL.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    chunks = results["documents"][0]
    metas = results["metadatas"][0]
    return list(zip(chunks, metas))