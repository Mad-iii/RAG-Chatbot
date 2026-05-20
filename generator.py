import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a research assistant answering questions based on document excerpts provided to you.

RULES:
- Base your answer primarily on the provided context chunks
- You may use reasoning and inference to connect ideas across chunks
- If something is genuinely not mentioned anywhere in the context, say: "This is not covered in the provided documents."
- Do NOT invent specific facts, numbers, or citations not present in the context
- Always reference which source/page you are drawing from when possible
- If asked to summarise multiple documents, summarise each source separately based on the chunks you have"""

def generate_answer(query, context_chunks):
    if not context_chunks:
        return "No documents have been indexed yet. Please upload and index a PDF first."

    context = "\n\n".join([
    f"[Source: {meta.get('title', meta['source'])}, Page {meta['page']}]\n{chunk}"  # ← title here
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