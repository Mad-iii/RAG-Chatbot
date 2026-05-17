import os
import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings

EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_store")
collection = client.get_or_create_collection("rag_docs")

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def ingest_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    filename = os.path.basename(pdf_path)
    all_chunks = []
    metadatas = []

    for page_num, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        chunks = chunk_text(text)
        for chunk in chunks:
            all_chunks.append(chunk)
            metadatas.append({"source": filename, "page": page_num + 1})

    embeddings = EMBED_MODEL.encode(all_chunks).tolist()
    ids = [f"{filename}_p{m['page']}_{i}" for i, m in enumerate(metadatas)]

    collection.add(
        documents=all_chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    print(f"✅ Ingested {len(all_chunks)} chunks from {filename}")

if __name__ == "__main__":
    for f in os.listdir("./docs"):
        if f.endswith(".pdf"):
            ingest_pdf(f"./docs/{f}")