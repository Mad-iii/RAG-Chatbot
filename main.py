import os, tempfile, json, glob
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

load_dotenv()

from ingest import ingest_pdf
from retriever import retrieve
from generator import generate_answer

app = FastAPI(title="Scholar")
app.mount("/static", StaticFiles(directory="static"), name="static")

DOCS_DIR = "docs"

@app.on_event("startup")
async def preload_docs():
    if not os.path.isdir(DOCS_DIR):
        return
    for pdf_path in glob.glob(os.path.join(DOCS_DIR, "*.pdf")):
        try:
            ingest_pdf(pdf_path)
            print(f"[Scholar] Pre-loaded: {os.path.basename(pdf_path)}")
        except Exception as e:
            print(f"[Scholar] Failed to pre-load {pdf_path}: {e}")

@app.get("/default-docs")
async def default_docs():
    if not os.path.isdir(DOCS_DIR):
        return JSONResponse({"docs": []})
    docs = []
    for p in glob.glob(os.path.join(DOCS_DIR, "*.pdf")):
        docs.append({"filename": os.path.basename(p)})
    return JSONResponse({"docs": docs})

@app.get("/static-doc")
async def static_doc(filename: str):
    path = os.path.join(DOCS_DIR, filename)
    if not os.path.isfile(path):
        raise HTTPException(404, "File not found")
    return FileResponse(path, media_type="application/pdf")

class QueryRequest(BaseModel):
    question: str

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("templates/index.html", encoding="utf-8") as f:
        return f.read()

@app.post("/upload")
async def upload(files: List[UploadFile] = File(...), titles: str = Form("")):
    title_map = {}
    try:
        title_map = json.loads(titles) if titles else {}
    except Exception:
        pass
    ingested = []
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(400, f"{file.filename} is not a PDF")
        content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            ingest_pdf(tmp_path, title_override=title_map.get(file.filename))
            ingested.append(file.filename)
        finally:
            os.unlink(tmp_path)
    return JSONResponse({"ingested": ingested})

@app.post("/query")
async def query(req: QueryRequest):
    def generate():
        chunks = retrieve(req.question)
        answer = generate_answer(req.question, chunks)
        words = answer.split(" ")
        for i, word in enumerate(words):
            token = word + ("" if i == len(words) - 1 else " ")
            yield json.dumps({"token": token}) + "\n"
        seen, sources = set(), []
        for _, meta in chunks:
            key = f"{meta.get('title', meta['source'])} · p{meta['page']}"  # ← title here
            if key not in seen:
                seen.add(key)
                sources.append(key)
        yield json.dumps({"done": True, "sources": sources}) + "\n"
    return StreamingResponse(generate(), media_type="application/x-ndjson")