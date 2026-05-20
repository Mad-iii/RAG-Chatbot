import os
from pypdf import PdfReader
from embedder import get_embed_model
from db import get_collection

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def ingest_pdf(pdf_path, title_override=None):
    reader = PdfReader(pdf_path)
    filename = os.path.basename(pdf_path)

    if title_override:
        title = title_override
    else:
        # Extract title from PDF metadata, fallback to filename without extension
        raw_title = (reader.metadata or {}).get("/Title", "").strip()
        title = raw_title if raw_title else os.path.splitext(filename)[0]

    all_chunks = []
    metadatas = []

    for page_num, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        chunks = chunk_text(text)
        for chunk in chunks:
            all_chunks.append(chunk)
            metadatas.append({"source": filename, "page": page_num + 1, "title": title})  # ← add title

    embeddings = get_embed_model().encode(all_chunks).tolist()
    ids = [f"{filename}_p{m['page']}_{i}" for i, m in enumerate(metadatas)]

    get_collection().add(
        documents=all_chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    print(f"[OK] Ingested {len(all_chunks)} chunks from {filename} (title: {title})")

if __name__ == "__main__":
    for f in os.listdir("./docs"):
        if f.endswith(".pdf"):
            ingest_pdf(f"./docs/{f}")