import streamlit as st
import tempfile
import os
from ingest import ingest_pdf
from retriever import retrieve
from generator import generate_answer

st.set_page_config(
    page_title="Scholar",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500&family=IBM+Plex+Serif:ital,wght@0,400;1,400&display=swap');

*, html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    box-sizing: border-box;
}

#MainMenu, footer, header { visibility: hidden; }

.stApp { background: #F7F6F3 !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E4E2DC !important;
}
[data-testid="stSidebar"] > div { padding: 2rem 1.25rem; }

.s-logo {
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 2rem;
}
.s-logo-icon { font-size: 18px; color: #3B5BDB; }
.s-logo-text {
    font-family: 'IBM Plex Serif', serif;
    font-size: 20px; color: #1A1A1A; letter-spacing: -0.3px;
}
.s-logo-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #3B5BDB; margin-bottom: 2px;
}

.s-label {
    font-size: 10px; font-weight: 500; letter-spacing: 1.5px;
    text-transform: uppercase; color: #9B9589; margin-bottom: 10px;
}
.s-rule { height: 1px; background: #E4E2DC; margin: 1.25rem 0; }

/* ── Upload box — nuke dark theme completely ── */
[data-testid="stFileUploader"] {
    background: #F0F3FF !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 0 !important;
}
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploader"] > div > div,
[data-testid="stFileUploaderDropzone"] {
    background: #F0F3FF !important;
    border: 1.5px dashed #93A8F4 !important;
    border-radius: 10px !important;
    color: #3B5BDB !important;
    padding: 1rem !important;
    text-align: center !important;
}
[data-testid="stFileUploader"] * {
    color: #3B5BDB !important;
    font-size: 12px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    background: transparent !important;
}
[data-testid="stFileUploader"] small {
    color: #9B9589 !important;
    font-size: 10px !important;
}
[data-testid="stFileUploader"] button {
    background: #FFFFFF !important;
    border: 1px solid #93A8F4 !important;
    color: #3B5BDB !important;
    border-radius: 6px !important;
    font-size: 11px !important;
    padding: 4px 14px !important;
    font-weight: 500 !important;
}
[data-testid="stFileUploader"] button:hover {
    background: #EEF2FF !important;
}
[data-testid="stFileUploader"] svg {
    fill: #748FFC !important;
    stroke: #748FFC !important;
}

/* ── Buttons ── */
.stButton > button {
    width: 100% !important;
    background: #3B5BDB !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 0.55rem 1rem !important;
    margin-top: 0.5rem !important;
    transition: background 0.15s !important;
}
.stButton > button:hover { background: #2F4AC7 !important; }

.ghost-btn .stButton > button {
    background: transparent !important;
    color: #9B9589 !important;
    border: 1px solid #E4E2DC !important;
    font-size: 11px !important;
    font-weight: 400 !important;
    margin-top: 0 !important;
}
.ghost-btn .stButton > button:hover {
    background: #F7F6F3 !important;
    color: #555 !important;
}

/* Doc rows */
.doc-row {
    display: flex; align-items: center; gap: 8px;
    padding: 7px 10px; border-radius: 7px;
    background: #F7F6F3; border: 1px solid #E4E2DC;
    margin-bottom: 5px;
}
.d-icon { font-size: 12px; color: #3B5BDB; flex-shrink: 0; }
.d-name { font-size: 11px; color: #555; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.d-live { width: 5px; height: 5px; border-radius: 50%; background: #2F9E44; flex-shrink: 0; }

.s-footer { font-size: 10px; color: #C0BDB6; line-height: 1.9; margin-top: 1.5rem; }

/* ── Main ── */
.block-container {
    padding-top: 0 !important;
    padding-bottom: 5.5rem !important;
    max-width: 780px !important;
}

.hero { padding: 4.5rem 1rem 2rem; max-width: 560px; }
.hero-tag {
    display: inline-block; font-size: 10px; font-weight: 500;
    letter-spacing: 1.5px; text-transform: uppercase;
    color: #3B5BDB; background: #EEF2FF;
    border-radius: 4px; padding: 3px 9px; margin-bottom: 1.2rem;
}
.hero-title {
    font-family: 'IBM Plex Serif', serif;
    font-size: 38px; color: #1A1A1A;
    line-height: 1.25; margin: 0 0 0.9rem; font-weight: 400;
}
.hero-title em { font-style: italic; color: #3B5BDB; }
.hero-desc {
    font-size: 14px; font-weight: 300;
    color: #6B6860; line-height: 1.75; margin: 0;
}

.chip-row {
    display: flex; flex-wrap: wrap; gap: 7px;
    margin: 2rem 1rem; max-width: 560px;
}
.chip {
    font-size: 12px; color: #555; background: #fff;
    border: 1px solid #E4E2DC; border-radius: 5px;
    padding: 5px 13px;
}

/* Messages */
.turn-spacer { height: 0.2rem; }

.msg-u { display: flex; justify-content: flex-end; margin: 0.5rem 0; padding: 0 0.25rem; }
.msg-u-inner {
    background: #3B5BDB; color: #fff;
    font-size: 14px; font-weight: 300; line-height: 1.65;
    border-radius: 12px 12px 3px 12px;
    padding: 11px 16px; max-width: 72%;
}

.msg-a { display: flex; gap: 11px; align-items: flex-start; margin: 0.5rem 0; padding: 0 0.25rem; }
.msg-a-av {
    width: 30px; height: 30px; border-radius: 7px;
    background: #EEF2FF; border: 1px solid #C5D0F5;
    display: flex; align-items: center; justify-content: center;
    font-family: 'IBM Plex Serif', serif; font-style: italic;
    font-size: 14px; color: #3B5BDB; flex-shrink: 0;
}
.msg-a-inner {
    background: #FFFFFF; border: 1px solid #E4E2DC;
    border-radius: 3px 12px 12px 12px;
    padding: 13px 16px; font-size: 14px; font-weight: 300;
    color: #2A2A2A; line-height: 1.8; max-width: 84%;
}

.src-row { margin: 5px 0 0 41px; padding: 0 0.25rem; }
.src-pill {
    display: inline-flex; align-items: center; gap: 4px;
    background: #F7F6F3; border: 1px solid #E4E2DC;
    border-radius: 4px; padding: 2px 9px;
    font-size: 10px; color: #9B9589;
    margin-right: 4px; margin-bottom: 3px;
}

/* ── Chat input — fix black bar ── */
div[data-testid="stBottom"] {
    background: #F7F6F3 !important;
    border-top: 1px solid #E4E2DC !important;
    padding: 0.75rem 1rem 1rem !important;
}

div[data-testid="stBottom"] > div {
    background: #F7F6F3 !important;
}

[data-testid="stChatInput"] {
    background: #FFFFFF !important;
    border: 1.5px solid #D8D5CF !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #3B5BDB !important;
    box-shadow: 0 0 0 3px rgba(59,91,219,0.1) !important;
}
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] > div > div {
    background: #FFFFFF !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important;
    color: #1A1A1A !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 14px !important; font-weight: 300 !important;
    caret-color: #3B5BDB !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #BFBDB6 !important;
    font-size: 14px !important;
}
[data-testid="stChatInput"] button {
    background: #3B5BDB !important;
    border-radius: 8px !important;
    border: none !important;
}
[data-testid="stChatInput"] button:hover {
    background: #2F4AC7 !important;
}

.input-hint {
    text-align: center; font-size: 10px;
    color: #C0BDB6; margin-top: 0.35rem; letter-spacing: 0.3px;
}

.stSuccess {
    background: #F3FFF3 !important;
    border: 1px solid #C3E6C3 !important;
    color: #2F6830 !important;
    border-radius: 7px !important; font-size: 13px !important;
}

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #CFCDC6; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ── State ──
if "messages" not in st.session_state:
    st.session_state.messages = []
if "docs_ingested" not in st.session_state:
    st.session_state.docs_ingested = []

# ══════════════════
# SIDEBAR
# ══════════════════
with st.sidebar:
    st.markdown("""
    <div class="s-logo">
        <span class="s-logo-icon">◈</span>
        <span class="s-logo-text">Scholar</span>
        <span class="s-logo-dot"></span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="s-label">Upload PDF</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
    "",                         
    type=["pdf"],
    accept_multiple_files=True,
    label_visibility="hidden" 
)

    if uploaded_files:
        if st.button("↑  Index Documents"):
            with st.spinner("Indexing…"):
                for f in uploaded_files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(f.read())
                        tmp_path = tmp.name
                    ingest_pdf(tmp_path)
                    os.unlink(tmp_path)
                    if f.name not in st.session_state.docs_ingested:
                        st.session_state.docs_ingested.append(f.name)
            st.success("Ready to query.")

    if st.session_state.docs_ingested:
        st.markdown('<div class="s-rule"></div>', unsafe_allow_html=True)
        st.markdown('<div class="s-label">Indexed</div>', unsafe_allow_html=True)
        for doc in st.session_state.docs_ingested:
            short = doc[:24] + "…" if len(doc) > 24 else doc
            st.markdown(f"""
            <div class="doc-row">
                <span class="d-icon">◈</span>
                <span class="d-name">{short}</span>
                <span class="d-live"></span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="s-rule"></div>', unsafe_allow_html=True)

    st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="s-footer">
        Answers sourced strictly<br>from your documents.<br>
        Groq · ChromaDB · MiniLM
    </div>
    """, unsafe_allow_html=True)

# ══════════════════
# MAIN
# ══════════════════
if not st.session_state.messages:
    st.markdown("""
    <div class="hero">
        <div class="hero-tag">RAG · Document QA</div>
        <div class="hero-title">Ask your<br><em>documents</em> anything.</div>
        <div class="hero-desc">Upload a PDF and ask questions in plain English. Every answer is pulled directly from your document — cited by page, no hallucination.</div>
    </div>
    <div class="chip-row">
        <div class="chip">Summarise the paper</div>
        <div class="chip">What problem does it solve?</div>
        <div class="chip">Key contributions</div>
        <div class="chip">Explain the method</div>
        <div class="chip">Results &amp; findings</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="msg-u">
                <div class="msg-u-inner">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-a">
                <div class="msg-a-av">s</div>
                <div class="msg-a-inner">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
            if "sources" in msg and msg["sources"]:
                seen = set()
                pills = ""
                for _, meta in msg["sources"]:
                    key = f"{meta['source']} · p{meta['page']}"
                    if key not in seen:
                        seen.add(key)
                        pills += f'<span class="src-pill">↗ {key}</span>'
                st.markdown(f'<div class="src-row">{pills}</div>', unsafe_allow_html=True)
        st.markdown('<div class="turn-spacer"></div>', unsafe_allow_html=True)

# ── Input ──
if query := st.chat_input("Ask something about your documents…"):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.spinner("Thinking…"):
        chunks = retrieve(query)
        answer = generate_answer(query, chunks)
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": chunks
    })
    st.rerun()

st.markdown('<div class="input-hint">Scholar answers only from your indexed documents</div>', unsafe_allow_html=True)