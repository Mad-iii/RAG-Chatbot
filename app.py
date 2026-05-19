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
<div class="g-blob g-blob-1"></div><div class="g-blob g-blob-2"></div><div class="g-blob g-blob-3"></div><div class="g-noise"></div>
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700&display=swap');
*, html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Outfit', -apple-system, sans-serif;
    box-sizing: border-box;
}
#MainMenu, footer, header { visibility: hidden; }
.stApp {
    background: radial-gradient(circle at 50% 50%, #0d0b21 0%, #05040a 100%) !important;
}
[data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: transparent !important;
}
.g-blob {
    position: fixed;
    border-radius: 50%;
    filter: blur(140px);
    z-index: -2;
    opacity: 0.35;
    pointer-events: none;
    animation: float-blob 22s infinite alternate ease-in-out;
}
.g-blob-1 {
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(138,43,226,0.5) 0%, rgba(0,0,0,0) 70%);
    top: 5%;
    left: 15%;
}
.g-blob-2 {
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(0,191,255,0.4) 0%, rgba(0,0,0,0) 70%);
    bottom: 10%;
    right: 10%;
    animation-delay: -6s;
}
.g-blob-3 {
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(0,245,212,0.3) 0%, rgba(0,0,0,0) 70%);
    bottom: 35%;
    left: 30%;
    animation-delay: -12s;
}
@keyframes float-blob {
    0% { transform: translate(0, 0) scale(1); }
    100% { transform: translate(60px, 40px) scale(1.15); }
}
.g-noise {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
    opacity: 0.02;
    pointer-events: none;
    z-index: -1;
}
h1, h2, h3, h4, h5, h6, p, span, label, small {
    color: rgba(255, 255, 255, 0.95) !important;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}
.stApp > div, [data-stale], [data-testid="stMarkdownContainer"] {
    opacity: 1 !important;
}
[data-testid="stSidebar"] {
    background: rgba(13, 11, 33, 0.45) !important;
    backdrop-filter: blur(24px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
}
[data-testid="stSidebar"] > div { padding: 2.2rem 1.4rem; }
.s-logo {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 2.5rem;
}
.s-logo-icon { font-size: 22px; color: #00d2ff; text-shadow: 0 0 15px rgba(0,210,255,0.6); }
.s-logo-text {
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    font-size: 22px; color: #ffffff; letter-spacing: -0.3px;
}
.s-logo-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #00d2ff; box-shadow: 0 0 10px #00d2ff;
    margin-bottom: -2px;
}
.s-label {
    font-size: 11px; font-weight: 600; letter-spacing: 1.8px;
    text-transform: uppercase; color: rgba(255, 255, 255, 0.5) !important; margin-bottom: 12px;
}
.s-rule { height: 1px; background: rgba(255, 255, 255, 0.1); margin: 1.5rem 0; }
[data-testid="stFileUploader"], [data-testid="stFileUploader"] > div, [data-testid="stFileUploader"] > div > div {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    border-radius: 0 !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: rgba(255, 255, 255, 0.04) !important;
    backdrop-filter: blur(20px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
    border: 1.5px dashed rgba(255, 255, 255, 0.2) !important;
    border-radius: 16px !important;
    padding: 1.5rem 1.2rem !important;
    width: 100% !important;
    min-height: 120px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    box-sizing: border-box !important;
    margin: 0 !important;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.2);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    animation: border-pulse 4s infinite ease-in-out;
}
@keyframes border-pulse {
    0%, 100% { border-color: rgba(255, 255, 255, 0.2); box-shadow: inset 0 2px 10px rgba(0,0,0,0.2), 0 0 0 rgba(0,210,255,0); }
    50% { border-color: rgba(0, 210, 255, 0.4); box-shadow: inset 0 2px 10px rgba(0,0,0,0.2), 0 0 15px rgba(0,210,255,0.15); }
}
[data-testid="stFileUploaderDropzone"]:hover {
    background: rgba(255, 255, 255, 0.08) !important;
    border-color: rgba(0, 210, 255, 0.5) !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.1);
}
[data-testid="stFileUploaderDropzone"] > div, [data-testid="stFileUploaderDropzone"] > div > div {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 auto !important;
    width: auto !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
}
[data-testid="stFileUploader"] * {
    color: rgba(255, 255, 255, 0.9) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: transparent !important;
}
[data-testid="stFileUploader"] small {
    color: rgba(255, 255, 255, 0.45) !important;
    font-size: 10px !important;
}
[data-testid="stFileUploaderDropzone"] svg {
    fill: #00d2ff !important;
    stroke: #00d2ff !important;
    animation: bounce-icon 3s infinite ease-in-out;
}
@keyframes bounce-icon {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
}
[data-testid="stFileUploaderDropzone"] > div > div:first-child {
    display: none !important;
}
[data-testid="stFileUploaderDropzone"] button p {
    font-size: 0 !important;
    line-height: 0 !important;
    color: transparent !important;
    margin: 0 !important;
}
[data-testid="stFileUploaderDropzone"] button p::after {
    content: "Browse file";
    font-size: 12px !important;
    color: #ffffff !important;
    line-height: normal !important;
}
[data-testid="stFileUploaderDropzone"] > div > div > div > button > div > p, [data-testid="stFileUploaderDropzone"] > div > div > div > button > div > div > p {
    display: none !important;
}
[data-testid="stFileUploaderDropzone"] button span span span {
    display: none !important;
}
[data-testid="stFileUploader"] button {
    background: rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    padding: 6px 16px !important;
    font-weight: 500 !important;
    margin: 0 auto !important;
    display: block !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    transition: all 0.25s ease !important;
}
[data-testid="stFileUploader"] button:hover {
    background: rgba(255, 255, 255, 0.15) !important;
    border-color: rgba(255, 255, 255, 0.35) !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.25);
}
.stButton > button {
    width: 100% !important;
    background: rgba(0, 210, 255, 0.15) !important;
    backdrop-filter: blur(15px) !important;
    -webkit-backdrop-filter: blur(15px) !important;
    color: #ffffff !important;
    border: 1px solid rgba(0, 210, 255, 0.3) !important;
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 0.65rem 1.2rem !important;
    margin-top: 0.5rem !important;
    box-shadow: 0 4px 20px rgba(0, 210, 255, 0.15), inset 0 1px 0 rgba(255,255,255,0.15);
    overflow: hidden;
    position: relative;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.stButton > button::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transition: 0.5s;
}
.stButton > button:hover::before {
    left: 100%;
}
.stButton > button:hover {
    background: rgba(0, 210, 255, 0.25) !important;
    border-color: rgba(0, 210, 255, 0.5) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0, 210, 255, 0.25), inset 0 1px 0 rgba(255,255,255,0.25) !important;
}
.stButton > button:active {
    transform: translateY(1px) !important;
}
.ghost-btn .stButton > button {
    background: rgba(255, 255, 255, 0.05) !important;
    color: rgba(255, 255, 255, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    font-size: 11px !important;
    font-weight: 400 !important;
    margin-top: 0 !important;
    box-shadow: none !important;
}
.ghost-btn .stButton > button:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #ffffff !important;
    border-color: rgba(255, 255, 255, 0.25) !important;
}
.doc-row {
    display: flex; align-items: center; gap: 10px;
    padding: 9px 12px; border-radius: 10px;
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    margin-bottom: 7px;
    transition: all 0.25s ease;
}
.doc-row:hover {
    background: rgba(255, 255, 255, 0.08) !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
    transform: translateX(3px);
}
.d-icon { font-size: 13px; color: #00d2ff; flex-shrink: 0; }
.d-name {
    font-size: 12px; color: rgba(255, 255, 255, 0.8) !important; flex: 1;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.d-live {
    width: 6px; height: 6px; border-radius: 50%;
    background: #00f5d4; box-shadow: 0 0 8px #00f5d4;
    flex-shrink: 0;
}
.s-footer {
    font-size: 10px; color: rgba(255, 255, 255, 0.3) !important; line-height: 2; margin-top: 2rem;
}
.block-container {
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(25px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(25px) saturate(180%) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 24px !important;
    padding: 3rem !important;
    margin-top: 4rem !important;
    margin-bottom: 5rem !important;
    max-width: 800px !important;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
}
.hero {
    margin-bottom: 2rem !important;
    position: relative;
    overflow: hidden;
}
.hero-tag {
    display: inline-block; font-size: 10px; font-weight: 600;
    letter-spacing: 2px; text-transform: uppercase;
    color: #00d2ff; background: rgba(0, 210, 255, 0.15);
    border: 1px solid rgba(0, 210, 255, 0.25);
    border-radius: 6px; padding: 4px 10px; margin-bottom: 1.5rem;
    text-shadow: 0 0 10px rgba(0,210,255,0.3);
}
.hero-title {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 40px; color: #ffffff !important;
    line-height: 1.25; margin: 0 0 1.2rem;
    text-shadow: 0 4px 15px rgba(0,0,0,0.5);
}
.hero-title em { font-style: italic; color: #00d2ff; text-shadow: 0 0 15px rgba(0,210,255,0.4); }
.hero-desc {
    font-size: 15px; font-weight: 300;
    color: rgba(255, 255, 255, 0.7) !important; line-height: 1.8; margin: 0;
}
.chip-row {
    display: flex; flex-wrap: wrap; gap: 10px;
    margin: 2rem 0;
}
.chip {
    font-size: 13px; color: rgba(255, 255, 255, 0.8) !important;
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 10px;
    padding: 8px 16px;
    cursor: pointer;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.chip:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    border-color: rgba(255, 255, 255, 0.25) !important;
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.2), 0 0 10px rgba(255,255,255,0.05);
}
.turn-spacer { height: 0.5rem; }
.msg-u {
    display: flex; justify-content: flex-end;
    margin: 0.8rem 0; padding: 0;
}
.msg-u-inner {
    background: rgba(0, 210, 255, 0.12) !important;
    backdrop-filter: blur(20px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
    border: 1px solid rgba(0, 210, 255, 0.3) !important;
    color: #ffffff !important;
    font-size: 15px; font-weight: 400; line-height: 1.7;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px; max-width: 75%;
    box-shadow: 0 6px 20px rgba(0, 210, 255, 0.08), inset 0 1px 0 rgba(255,255,255,0.15);
    animation: slide-up-bubble 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.msg-a {
    display: flex; gap: 14px; align-items: flex-start;
    margin: 0.8rem 0; padding: 0;
}
.msg-a-av {
    width: 32px; height: 32px; border-radius: 10px;
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    backdrop-filter: blur(10px) !important;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Outfit', sans-serif; font-weight: 600;
    font-size: 14px; color: #00d2ff; flex-shrink: 0;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    text-shadow: 0 0 5px rgba(0,210,255,0.3);
}
.msg-a-inner {
    background: rgba(255, 255, 255, 0.06) !important;
    backdrop-filter: blur(20px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 4px 18px 18px 18px;
    padding: 14px 20px; font-size: 15px; font-weight: 300;
    color: rgba(255, 255, 255, 0.95) !important; line-height: 1.8; max-width: 82%;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    animation: slide-up-bubble 0.45s cubic-bezier(0.4, 0, 0.2, 1);
}
@keyframes slide-up-bubble {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
.src-row { margin: 6px 0 0 46px; padding: 0; }
.src-pill {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(8px) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 6px; padding: 3px 10px;
    font-size: 11px; color: rgba(255, 255, 255, 0.45) !important;
    margin-right: 6px; margin-bottom: 4px;
    transition: all 0.2s ease;
}
.src-pill:hover {
    background: rgba(0, 210, 255, 0.1) !important;
    border-color: rgba(0, 210, 255, 0.3) !important;
    color: #ffffff !important;
}
div[data-testid="stBottom"] {
    background: transparent !important;
    border-top: none !important;
    padding: 1rem 1rem 1.5rem !important;
    will-change: unset !important;
}
div[data-testid="stBottom"] > div {
    background: transparent !important;
}
[data-testid="stChatInput"] {
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(24px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 16px !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255,255,255,0.15) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(0, 210, 255, 0.4) !important;
    box-shadow: 0 10px 30px rgba(0, 210, 255, 0.15), inset 0 1px 0 rgba(255,255,255,0.2) !important;
}
[data-testid="stChatInput"] > div, [data-testid="stChatInput"] > div > div {
    background: transparent !important;
    border-radius: 16px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #ffffff !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 15px !important;
    font-weight: 300 !important;
    caret-color: #00d2ff !important;
    padding-top: 12px !important;
    padding-bottom: 12px !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(255, 255, 255, 0.35) !important;
    font-size: 15px !important;
}
[data-testid="stChatInput"] button {
    background: rgba(0, 210, 255, 0.2) !important;
    border-radius: 10px !important;
    border: 1px solid rgba(0, 210, 255, 0.3) !important;
    transition: all 0.2s ease !important;
}
[data-testid="stChatInput"] button:hover {
    background: rgba(0, 210, 255, 0.4) !important;
    border-color: rgba(0, 210, 255, 0.6) !important;
}
.input-hint {
    text-align: center; font-size: 11px;
    color: rgba(255, 255, 255, 0.3) !important; margin-top: 0.5rem; letter-spacing: 0.5px;
}
.stSuccess {
    background: rgba(0, 245, 212, 0.1) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(0, 245, 212, 0.3) !important;
    color: #00f5d4 !important;
    border-radius: 12px !important;
    font-size: 13px !important;
    box-shadow: 0 4px 15px rgba(0, 245, 212, 0.05);
}
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 3px;
    border: 1px solid rgba(255,255,255,0.05);
}
::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.25); }
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

    # Render user bubble immediately — no rerun needed
    st.markdown(f"""
    <div class="msg-u">
        <div class="msg-u-inner">{query}</div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Thinking…"):
        chunks = retrieve(query)
        answer = generate_answer(query, chunks)

    msg = {"role": "assistant", "content": answer, "sources": chunks}
    st.session_state.messages.append(msg)

    # Render assistant bubble immediately — no rerun needed
    st.markdown(f"""
    <div class="msg-a">
        <div class="msg-a-av">s</div>
        <div class="msg-a-inner">{answer}</div>
    </div>
    """, unsafe_allow_html=True)

    if chunks:
        seen = set()
        pills = ""
        for _, meta in chunks:
            key = f"{meta['source']} · p{meta['page']}"
            if key not in seen:
                seen.add(key)
                pills += f'<span class="src-pill">↗ {key}</span>'
        st.markdown(f'<div class="src-row">{pills}</div>', unsafe_allow_html=True)

st.markdown('<div class="input-hint">Scholar answers only from your indexed documents</div>', unsafe_allow_html=True)