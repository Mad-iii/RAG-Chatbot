---
title: Scholar RAG Agent
emoji: 📚
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# ◈ Scholar — RAG Document QA

> Upload a PDF. Ask questions in plain English. Every answer is pulled directly from your document, cited by page — no hallucination.

![Python](https://img.shields.io/badge/Python-3.10+-3B5BDB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

---

## What is Scholar?

Scholar is a Retrieval-Augmented Generation (RAG) chatbot that lets you have a conversation with your PDF documents. It chunks and embeds your files into a persistent vector store, then retrieves the most relevant passages at query time and feeds them — with strict source constraints — to a fast LLM via Groq.

Answers are grounded entirely in your documents. If the answer isn't there, Scholar says so.

---

## How it works
PDF Upload
│
▼
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│  ingest.py  │────▶│  ChromaDB Store  │────▶│ retriever.py│
│  pypdf +    │     │  (persistent,    │     │ top-k cosine│
│  MiniLM     │     │   ./chroma_store)│     │ similarity  │
└─────────────┘     └──────────────────┘     └──────┬──────┘
│
┌──────▼──────┐
│ generator.py│
│ Groq LLaMA  │
│ 3.3 70B     │
└──────┬──────┘
│
Cited answer
(source + page №)
1. **Ingest** — `pypdf` extracts text page by page; text is split into 500-word overlapping chunks; `all-MiniLM-L6-v2` encodes each chunk into a 384-dim embedding stored in ChromaDB.
2. **Retrieve** — at query time, the same model embeds the question and ChromaDB returns the top-k most similar chunks with their source metadata.
3. **Generate** — chunks are assembled into a context block and sent to `llama-3.3-70b-versatile` on Groq with a strict system prompt: answer only from the provided context, always cite source and page.

---

## Features

- **Strict grounding** — the LLM is instructed never to use training knowledge; it cites exact source filenames and page numbers or refuses to answer
- **Multi-document support** — index several PDFs in one session; each chunk carries its filename, title, and page as metadata
- **Persistent vector store** — ChromaDB stores embeddings on disk (`./chroma_store`), so re-indexing is not required on restart
- **Fast inference** — Groq's hosted LLaMA 3.3 70B delivers sub-second responses
- **Streaming responses** — answers stream token by token via NDJSON for a real-time feel
- **Pre-loadable docs** — drop PDFs into the `docs/` folder and they are auto-ingested on startup

---

## Project structure
RAG-Chatbot/
├── main.py           # FastAPI app — upload, query, static serving
├── ingest.py         # PDF → chunks → embeddings → ChromaDB
├── retriever.py      # Query embedding → ChromaDB top-k lookup
├── generator.py      # Context assembly → Groq LLaMA → cited answer
├── embedder.py       # Shared SentenceTransformer model (lazy loaded)
├── db.py             # ChromaDB client and collection singleton
├── templates/
│   └── index.html    # Frontend UI
├── static/           # Static assets (CSS, JS)
├── docs/             # (optional) drop PDFs here for auto-ingest on startup
├── Dockerfile        # Docker config for HuggingFace Spaces deployment
├── requirements.txt  # Python dependencies
└── .gitignore
---

## Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/Mad-iii/RAG-Chatbot.git
cd RAG-Chatbot
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Groq API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get a free API key at [console.groq.com](https://console.groq.com).

### 5. Run the app

```bash
uvicorn main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## Usage

1. Click **Upload PDF** and select one or more PDF files.
2. Scholar chunks, embeds, and stores them in ChromaDB automatically.
3. Type a question in the chat input.
4. Scholar retrieves the relevant passages and streams back a cited answer with source and page number.

---

## Deployment

This app is deployed on **HuggingFace Spaces** using Docker.

Set your `GROQ_API_KEY` under **Settings → Variables and Secrets** in your Space.

---

## Configuration

| Parameter | Location | Default | Description |
|-----------|----------|---------|-------------|
| Chunk size | `ingest.py` | `500` words | Words per chunk |
| Chunk overlap | `ingest.py` | `50` words | Overlap between adjacent chunks |
| Top-k retrieval | `retriever.py` | `5` | Chunks returned per query |
| Max per source | `retriever.py` | `3` | Max chunks per PDF for diversity |
| LLM model | `generator.py` | `llama-3.3-70b-versatile` | Groq model ID |
| Temperature | `generator.py` | `0.2` | Lower = more factual |
| Embedding model | `embedder.py` | `all-MiniLM-L6-v2` | Sentence-Transformers model |

---

## Tech stack

| Layer | Library |
|-------|---------|
| Backend | [FastAPI](https://fastapi.tiangolo.com) |
| PDF parsing | [pypdf](https://pypdf.readthedocs.io) |
| Embeddings | [sentence-transformers](https://www.sbert.net) · `all-MiniLM-L6-v2` |
| Vector store | [ChromaDB](https://www.trychroma.com) (persistent) |
| LLM inference | [Groq](https://groq.com) · LLaMA 3.3 70B Versatile |
| Deployment | [HuggingFace Spaces](https://huggingface.co/spaces) · Docker |
| Env management | [python-dotenv](https://pypi.org/project/python-dotenv) |

---

## Limitations

- Only PDF files are supported at this time.
- The vector store is shared across all users in the deployed Space.
- Very large PDFs (500+ pages) may take a moment to index on first upload.

---

## License

MIT — free to use, modify, and distribute.
