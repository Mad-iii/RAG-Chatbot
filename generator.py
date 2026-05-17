import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a research assistant. You have been given context extracted from specific documents.

STRICT RULES:
- Answer ONLY using the provided context
- If the answer is not in the context, say exactly: "This information is not in the provided documents."
- NEVER use your general training knowledge to fill gaps
- NEVER make up sources, page numbers, or citations
- Always cite the exact source and page number from the context"""
def generate_answer(query, context_chunks):
    context = "\n\n".join([
        f"[Source: {meta['source']}, Page {meta['page']}]\n{chunk}"
        for chunk, meta in context_chunks
    ])

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content