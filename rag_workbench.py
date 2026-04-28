"""
app.py — AI Architecture Workbench (Professional UI Rewrite)
─────────────────────────────────────────────────────────────────────────────
Run:  streamlit run app.py
─────────────────────────────────────────────────────────────────────────────
"""

import streamlit as st
import os
import re
import json
import base64
import requests
from streamlit_mermaid import st_mermaid

# ── Lazy imports for LangChain / Chroma ────────────────────────────────────
try:
    from langchain_ollama import OllamaEmbeddings
    from langchain_chroma import Chroma
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    LANGCHAIN_OK = True
except ImportError:
    LANGCHAIN_OK = False

# ── CONFIGURATION ──────────────────────────────────────────────────────────
MODEL_NAME       = "mistral"
EMBEDDING_MODEL  = "nomic-embed-text"
PDF_DIRECTORY    = "course_materials"
VECTOR_STORE_DIR = "./chroma_db"

PROVIDERS = {
    "local":    ("Local",     [MODEL_NAME]),
    "gemini":   ("Gemini",    ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]),
    "claude":   ("Claude",    ["claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022", "claude-3-opus-20240229"]),
    "deepseek": ("DeepSeek",  ["deepseek-chat", "deepseek-reasoner"]),
    "openai":   ("OpenAI",    ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"]),
}

# ── THEME ──────────────────────────────────────────────────────────────────

def build_css(dark: bool) -> str:
    if dark:
        v = dict(
            page_bg="#0C0E12", surface="#13161E", surface2="#191D28", surface3="#1E2333",
            border="#252B3B", border2="#2D3448",
            text="#E8EAF0", text2="#8B91A8", text3="#525870",
            accent="#5B5BD6", accent_dim="#3D3D9E",
            accent_glow="rgba(91,91,214,0.18)", accent_fg="#A5A8F0",
            green="#34D399", green_bg="rgba(52,211,153,0.10)", green_fg="#6EE7B7",
            blue="#60A5FA",  blue_bg="rgba(96,165,250,0.10)",  blue_fg="#93C5FD",
            purple="#A78BFA",purple_bg="rgba(167,139,250,0.10)",purple_fg="#C4B5FD",
            red="#F87171",   red_bg="rgba(248,113,113,0.10)",  red_fg="#FCA5A5",
            amber="#FBBF24", amber_bg="rgba(251,191,36,0.10)", amber_fg="#FCD34D",
            code_bg="#080A0F", btn_text="#FFFFFF", hr_color="#1E2333",
            shadow="rgba(0,0,0,0.4)",
        )
    else:
        v = dict(
            page_bg="#F8F9FA", surface="#FFFFFF", surface2="#F1F5F9", surface3="#E2E8F0",
            border="#E2E8F0", border2="#CBD5E1",
            text="#0F172A", text2="#334155", text3="#64748B",
            accent="#2563EB", accent_dim="#1D4ED8",
            accent_glow="rgba(37,99,235,0.1)", accent_fg="#2563EB",
            green="#059669", green_bg="#ECFDF5", green_fg="#065F46",
            blue="#2563EB",  blue_bg="#EFF6FF",  blue_fg="#1E3A8A",
            purple="#7C3AED",purple_bg="#F5F3FF",purple_fg="#4C1D95",
            red="#DC2626",   red_bg="#FEF2F2",   red_fg="#7F1D1D",
            amber="#D97706", amber_bg="#FFFBEB", amber_fg="#78350F",
            code_bg="#1E293B", btn_text="#FFFFFF", hr_color="#E2E8F0",
            shadow="rgba(0,0,0,0.05)",
        )

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500&family=Instrument+Sans:wght@400;500;600&display=swap');

#MainMenu, footer, header, .stDeployButton, [data-testid="stToolbar"] {{ visibility: hidden !important; height: 0 !important; }}

html, body, [data-testid="stAppViewContainer"] {{
    background: {v['page_bg']} !important;
    color: {v['text']} !important;
    font-family: 'Instrument Sans', sans-serif !important;
}}
[data-testid="stAppViewContainer"] > .main {{ background: {v['page_bg']}; padding: 0 2.5rem 3rem; }}
[data-testid="stSidebar"] {{ background: {v['surface']} !important; border-right: 1px solid {v['border']} !important; }}

/* ── Header ── */
.wb-shell {{ padding-top: 2rem; padding-bottom: 0.5rem; }}
.wb-header {{ display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 0; }}
.wb-wordmark {{ display: flex; align-items: center; gap: 0.75rem; }}
.wb-logo {{ width: 36px; height: 36px; background: {v['accent']}; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
.wb-logo svg {{ width: 20px; height: 20px; fill: #fff; }}
.wb-title {{ font-family: 'Syne', sans-serif; font-size: 1.35rem; font-weight: 700; color: {v['text']}; margin: 0; letter-spacing: -0.03em; line-height: 1.2; }}
.wb-tagline {{ font-style: italic; font-size: 0.82rem; color: {v['text2']}; margin-top: 0.2rem; opacity: 0.8; }}
.wb-sub {{ color: {v['text3']}; font-size: 0.67rem; font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.04em; margin-top: 0.18rem; }}
.wb-divider {{ border: none; border-top: 1px solid {v['hr_color']}; margin: 0.85rem 0 1.1rem; }}

/* ── Status ── */
.status-chip {{ display: inline-flex; align-items: center; gap: 0.4rem; background: {v['green_bg']}; border: 1px solid {v['green']}; border-radius: 100px; padding: 0.2rem 0.65rem; font-size: 0.68rem; font-weight: 600; color: {v['green']}; letter-spacing: 0.03em; margin-bottom: 1.1rem; }}
.status-dot {{ width: 6px; height: 6px; border-radius: 50%; background: {v['green']}; animation: pulse 2s ease-in-out infinite; }}
@keyframes pulse {{ 0%, 100% {{ opacity: 1; transform: scale(1); }} 50% {{ opacity: 0.6; transform: scale(0.85); }} }}

/* ── Panels ── */
.panel {{ background: {v['surface']}; border: 1px solid {v['border']}; border-radius: 12px; padding: 1.1rem 1.25rem; margin-bottom: 0.85rem; box-shadow: 0 1px 4px {v['shadow']}; transition: border-color 0.2s; }}
.panel:hover {{ border-color: {v['border2']}; }}
.panel-label {{ font-family: 'IBM Plex Mono', monospace; color: {v['text3']}; font-size: 0.62rem; font-weight: 500; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.65rem; }}

/* ── Empty state ── */
.empty-state {{ text-align: center; padding: 4rem 2rem; background: {v['surface']}; border: 1px dashed {v['border2']}; border-radius: 12px; }}
.empty-icon {{ width: 48px; height: 48px; margin: 0 auto 1rem; background: {v['surface2']}; border-radius: 12px; display: flex; align-items: center; justify-content: center; }}
.empty-icon svg {{ width: 24px; height: 24px; stroke: {v['text3']}; fill: none; stroke-width: 1.5; }}
.empty-title {{ font-family: 'Syne', sans-serif; font-size: 0.95rem; font-weight: 600; color: {v['text2']}; margin-bottom: 0.35rem; }}
.empty-sub {{ font-size: 0.78rem; color: {v['text3']}; line-height: 1.6; }}

/* ── Arch badge ── */
.arch-badge {{ display: inline-flex; align-items: center; gap: 0.45rem; background: {v['accent_glow']}; border: 1.5px solid {v['accent']}; color: {v['accent_fg']}; font-family: 'Syne', sans-serif; font-size: 0.88rem; font-weight: 700; padding: 0.35rem 1rem; border-radius: 6px; letter-spacing: -0.01em; }}
.arch-badge::before {{ content: ''; width: 8px; height: 8px; border-radius: 2px; background: {v['accent']}; display: inline-block; opacity: 0.8; }}
.just-box {{ background: {v['surface2']}; border-left: 3px solid {v['accent']}; border-radius: 0 8px 8px 0; padding: 0.8rem 1rem; font-size: 0.82rem; color: {v['text2']}; line-height: 1.7; margin-top: 0.6rem; }}

/* ── Tags ── */
.tags {{ display: flex; flex-wrap: wrap; gap: 0.35rem; }}
.tag {{ border-radius: 5px; font-size: 0.67rem; font-weight: 600; font-family: 'IBM Plex Mono', monospace; padding: 0.22rem 0.6rem; border: 1px solid; letter-spacing: 0.01em; }}
.tag-grey   {{ background: {v['surface2']}; border-color: {v['border2']}; color: {v['text2']}; }}
.tag-green  {{ background: {v['green_bg']};  border-color: {v['green']};  color: {v['green_fg']};  }}
.tag-blue   {{ background: {v['blue_bg']};   border-color: {v['blue']};   color: {v['blue_fg']};   }}
.tag-purple {{ background: {v['purple_bg']}; border-color: {v['purple']}; color: {v['purple_fg']}; }}
.tag-red    {{ background: {v['red_bg']};    border-color: {v['red']};    color: {v['red_fg']};    }}
.tag-amber  {{ background: {v['amber_bg']};  border-color: {v['amber']};  color: {v['amber_fg']};  }}

/* ── Components ── */
.comp-row {{ display: grid; grid-template-columns: 160px 1fr auto; align-items: start; padding: 0.6rem 0; border-bottom: 1px solid {v['border']}; gap: 0.75rem; font-size: 0.79rem; }}
.comp-row:last-child {{ border-bottom: none; }}
.comp-name {{ color: {v['text']}; font-weight: 600; font-size: 0.8rem; }}
.comp-role {{ color: {v['text2']}; line-height: 1.5; }}
.comp-tech {{ color: {v['accent_fg']}; font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; white-space: nowrap; background: {v['accent_glow']}; border: 1px solid {v['accent']}; border-radius: 4px; padding: 0.15rem 0.45rem; }}

/* ── Stack grid ── */
.stack-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 0.5rem; margin-top: 0.25rem; }}
.stack-item {{ background: {v['surface2']}; border: 1px solid {v['border']}; border-radius: 8px; padding: 0.55rem 0.75rem; }}
.stack-layer {{ font-family: 'IBM Plex Mono', monospace; font-size: 0.58rem; color: {v['text3']}; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.2rem; }}
.stack-value {{ font-size: 0.75rem; font-weight: 600; color: {v['text']}; line-height: 1.3; }}

/* ── Risks ── */
.risk {{ display: flex; align-items: flex-start; gap: 0.6rem; background: {v['red_bg']}; border-left: 3px solid {v['red']}; border-radius: 0 7px 7px 0; padding: 0.5rem 0.8rem; font-size: 0.78rem; color: {v['red_fg']}; margin-bottom: 0.4rem; line-height: 1.5; }}

/* ── Mermaid code ── */
.mermaid-code {{ background: {v['code_bg']}; border: 1px solid {v['border']}; border-radius: 8px; padding: 0.85rem 1rem; font-family: 'IBM Plex Mono', monospace; font-size: 0.71rem; color: #7DD3FC; white-space: pre; overflow: auto; max-height: 210px; line-height: 1.6; }}
.live-btn {{ display: inline-flex; align-items: center; gap: 0.4rem; background: transparent; color: {v['accent_fg']} !important; border: 1px solid {v['accent']}; font-size: 0.72rem; font-weight: 600; font-family: 'Instrument Sans', sans-serif; padding: 0.35rem 0.85rem; border-radius: 6px; text-decoration: none !important; margin-top: 0.6rem; transition: background 0.15s; letter-spacing: 0.01em; }}
.live-btn:hover {{ background: {v['accent_glow']}; }}

/* ── Tips ── */
.tip-item {{ display: flex; align-items: flex-start; gap: 0.5rem; font-size: 0.76rem; color: {v['text3']}; line-height: 1.55; padding: 0.2rem 0; }}
.tip-bullet {{ width: 4px; height: 4px; border-radius: 50%; background: {v['text3']}; flex-shrink: 0; margin-top: 0.5rem; }}

/* ── Streamlit widget overrides ── */
.stButton > button {{ background: {v['accent']} !important; color: {v['btn_text']} !important; border: none !important; border-radius: 8px !important; padding: 0.6rem 1.5rem !important; font-family: 'Syne', sans-serif !important; font-size: 0.88rem !important; font-weight: 700 !important; letter-spacing: -0.01em !important; width: 100% !important; transition: all 0.18s !important; }}
.stButton > button:hover {{ background: {v['accent_dim']} !important; box-shadow: 0 4px 16px {v['accent_glow']} !important; }}
.stButton > button:disabled {{ opacity: 0.35 !important; }}

.stTextArea > div > div > textarea {{ background: {v['surface2']} !important; border: 1px solid {v['border']} !important; border-radius: 8px !important; color: {v['text']} !important; font-family: 'Instrument Sans', sans-serif !important; font-size: 0.83rem !important; line-height: 1.6 !important; }}
.stTextArea > div > div > textarea:focus {{ border-color: {v['accent']} !important; box-shadow: 0 0 0 3px {v['accent_glow']} !important; outline: none !important; }}

.stTextInput > div > div > input {{ background: {v['surface2']} !important; border: 1px solid {v['border']} !important; border-radius: 8px !important; color: {v['text']} !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 0.78rem !important; }}
.stTextInput > div > div > input:focus {{ border-color: {v['accent']} !important; box-shadow: 0 0 0 3px {v['accent_glow']} !important; }}

.stSelectbox > div > div {{ background: {v['surface2']} !important; border: 1px solid {v['border']} !important; border-radius: 8px !important; color: {v['text']} !important; font-family: 'Instrument Sans', sans-serif !important; }}
.stSelectbox svg {{ color: {v['text2']} !important; fill: {v['text2']} !important; opacity: 1 !important; }}

/* Status widget (generation progress) */
[data-testid="stStatusWidget"] {{
    background: {v['surface']} !important;
    border: 1px solid {v['border']} !important;
    border-radius: 10px !important;
    box-shadow: none !important;
}}
[data-testid="stStatusWidget"] [data-testid="stMarkdownContainer"] p {{
    color: {v['text']} !important;
}}
[data-testid="stStatusWidget"] [data-testid="stStatusWidgetLabel"] {{
    color: {v['text']} !important;
}}
[data-testid="stStatusWidget"] svg {{
    color: {v['accent']} !important;
}}

/* Provider Selector (Radio) */
.stRadio > div {{ 
    display: grid !important; 
    grid-template-columns: repeat(5, 1fr) !important; 
    gap: 10px !important; 
    background: {v['surface2']} !important; 
    border: 1px solid {v['border']} !important; 
    border-radius: 14px !important; 
    padding: 10px !important; 
}}

.stRadio > div > label {{ 
    min-width: 0 !important;
    width: 100% !important;
    height: 64px !important;
    padding: 8px 12px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 10px !important;
    border: 1px solid {v['border']} !important;
    border-radius: 12px !important; 
    background: {v['surface']} !important;
    color: {v['text2']} !important; 
    font-size: 0.76rem !important; 
    font-weight: 700 !important; 
    line-height: 1.15 !important;
    text-align: center !important; 
    cursor: pointer !important;
    box-sizing: border-box !important;
    transition: all 160ms ease !important;
}}

/* Clean custom indicator (replaces default radio dots) */
.stRadio > div > label::before {{
    content: "";
    width: 9px;
    height: 9px;
    border-radius: 999px;
    border: 1px solid {v['border2']};
    background: transparent;
    box-shadow: inset 0 0 0 2px transparent;
    flex: 0 0 auto;
    transition: all 160ms ease;
}}

.stRadio > div > label:hover {{
    background: {v['surface3']} !important;
    border-color: {v['border2']} !important;
    transform: translateY(-1px);
}}

/* Selected state using Streamlit's checkbox detection */
.stRadio > div > label:has(input:checked) {{ 
    background: {v['accent']} !important; 
    color: #FFFFFF !important; 
    border-color: {v['accent_dim']} !important;
    box-shadow: 0 8px 18px {v['accent_glow']} !important;
}}

.stRadio > div > label:has(input:checked)::before {{
    border-color: rgba(255,255,255,0.9);
    background: #FFFFFF;
    box-shadow: inset 0 0 0 2px {v['accent']};
}}

/* Force color on nested elements inside radio labels */
.stRadio > div > label p, 
.stRadio > div > label span,
.stRadio > div > label div {{ 
    color: inherit !important; 
    font-weight: inherit !important; 
    min-height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    white-space: normal;
    word-break: keep-all;
    line-height: 1.2;
}}

/* Radio Dot styling - hidden to keep cards clean */
.stRadio [data-testid="stRadioButton"],
.stRadio input[type="radio"] {{
    display: none !important;
}}

@media (max-width: 900px) {{
    .stRadio > div {{ grid-template-columns: repeat(3, 1fr) !important; }}
}}

@media (max-width: 560px) {{
    .stRadio > div {{ grid-template-columns: repeat(2, 1fr) !important; }}
    .stRadio > div > label {{ height: 56px !important; }}
}}

label[data-testid="stWidgetLabel"] {{ color: {v['text2']} !important; font-size: 0.7rem !important; font-family: 'IBM Plex Mono', monospace !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; }}
[data-testid="stExpander"] {{ background: {v['surface']} !important; border: 1px solid {v['border']} !important; border-radius: 10px !important; }}
.stSpinner > div {{ border-top-color: {v['accent']} !important; }}
.stCaption {{ color: {v['text3']} !important; font-size: 0.7rem !important; }}
[data-testid="column"] {{ padding: 0 0.5rem !important; }}
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {v['border2']}; border-radius: 3px; }}
</style>
"""


# ── HELPERS ────────────────────────────────────────────────────────────────

def get_mermaid_live_url(code: str) -> str:
    state = json.dumps({"code": code, "mermaid": {"theme": "dark"}})
    encoded = base64.urlsafe_b64encode(state.encode()).decode()
    return f"https://mermaid.live/edit#base64:{encoded}"


def sanitize_mermaid(code: str) -> str:
    sq_pattern  = re.compile(r'(\w+)\[([^"\]\[]+)\]')
    rnd_pattern = re.compile(r'(\b\w+)\(([^"()]+)\)')
    dia_pattern = re.compile(r'(\w+)\{([^"{}]+)\}')
    SPECIAL     = re.compile(r'[\s()/\-:,&]')

    def _quote(nid, ob, label, cb):
        label = label.strip()
        if SPECIAL.search(label):
            return f'{nid}{ob}"{label.replace(chr(34), "")}"{cb}'
        return f'{nid}{ob}{label}{cb}'

    lines = []
    for line in code.splitlines():
        if line.strip().startswith('%%'):
            continue
        line = re.sub(r'(?<!-)->(?!>)', '-->', line)
        line = re.sub(r'=>', '-->', line)
        line = sq_pattern.sub(lambda m: _quote(m.group(1), '[', m.group(2), ']'), line)
        line = rnd_pattern.sub(lambda m: _quote(m.group(1), '(', m.group(2), ')'), line)
        line = dia_pattern.sub(lambda m: _quote(m.group(1), '{', m.group(2), '}'), line)
        lines.append(line)

    result = '\n'.join(lines).strip()
    if result and not re.match(r'^(graph|flowchart|sequenceDiagram|classDiagram|gantt|pie)', result, re.I):
        result = 'graph TD\n' + result
    return result


def tags_html(items: list, css_class: str = "tag-grey") -> str:
    pills = "".join(f'<span class="tag {css_class}">{i}</span>' for i in items)
    return f'<div class="tags">{pills}</div>'


# ── RAG DOCUMENT LOADER ────────────────────────────────────────────────────

@st.cache_resource
def load_and_process_documents():
    if not LANGCHAIN_OK:
        return None
    if not os.path.exists(PDF_DIRECTORY) or not os.listdir(PDF_DIRECTORY):
        return None
    files = [f for f in os.listdir(PDF_DIRECTORY) if f.endswith(('.pdf', '.txt', '.md'))]
    if not files:
        return None

    pb = st.progress(0)
    status = st.empty()
    raw_docs = []
    for i, fname in enumerate(files):
        status.text(f"Reading {fname}…")
        fpath = os.path.join(PDF_DIRECTORY, fname)
        try:
            if fname.endswith(".pdf"):
                from langchain_community.document_loaders import PyPDFLoader
                raw_docs.extend(PyPDFLoader(fpath).load())
            else:
                from langchain_community.document_loaders import TextLoader
                raw_docs.extend(TextLoader(fpath, encoding="utf-8").load())
        except Exception as e:
            st.warning(f"Skipping {fname}: {e}")
        pb.progress((i + 1) / len(files) * 0.1)

    status.text("Splitting text…")
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)
    docs = splitter.split_documents(raw_docs)
    pb.progress(0.15)

    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    status.text(f"Building vector store from {len(docs)} chunks…")

    if os.path.exists(VECTOR_STORE_DIR) and os.listdir(VECTOR_STORE_DIR):
        vectorstore = Chroma(persist_directory=VECTOR_STORE_DIR, embedding_function=embeddings)
    else:
        vectorstore = None
        for i in range(0, len(docs), 50):
            batch = docs[i:i + 50]
            if vectorstore is None:
                vectorstore = Chroma.from_documents(batch, embedding=embeddings,
                                                    persist_directory=VECTOR_STORE_DIR)
            else:
                vectorstore.add_documents(batch)
            pb.progress(min(0.15 + (i / len(docs)) * 0.85, 1.0))

    status.empty(); pb.empty()
    return vectorstore


# ── LLM BACKENDS ──────────────────────────────────────────────────────────

_TEMPLATE = """\
You are an expert software architect. Use the context below to help design a system.

Context:
{context}

Requirements:
{question}

Reply ONLY with a JSON object — no markdown fences, no extra text.
{{
  "recommended_style": "Microservices | SOA | Layered | Event-Driven | Serverless | Monolith",
  "architecture_rationale": "2 sentences max",
  "functional_requirements": ["fr1","fr2","fr3"],
  "non_functional_requirements": ["nfr1","nfr2"],
  "quality_attributes": ["qa1","qa2"],
  "scalability_tactics": ["t1","t2"],
  "availability_tactics": ["t1","t2"],
  "security_tactics": ["t1","t2"],
  "components": [
    {{"name":"API Gateway","role":"Entry point & routing","technology":"Kong"}},
    {{"name":"Auth Service","role":"JWT / OAuth2","technology":"Keycloak"}}
  ],
  "tech_stack": {{"frontend":"React","backend":"FastAPI","database":"PostgreSQL","messaging":"Kafka","devops":"Docker + K8s"}},
  "deployment_recommendation": "one sentence",
  "risk_assessment": ["risk1","risk2"],
  "mermaid_diagram": "graph TD\\n  Client[\\"Web Client\\"] --> GW[\\"API Gateway\\"]\\n  GW --> Auth[\\"Auth Service\\"]\\n  GW --> Svc[\\"Core Service\\"]\\n  Svc --> DB[\\"Database\\"]"
}}
Mermaid rules: graph TD · --> arrows · quote labels with spaces/parens · no subgraph · min 5 nodes.\
"""


def _parse_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except Exception:
        pass
    m = re.search(r'\{.*\}', raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group())
        except Exception:
            pass
    return {"_raw": raw}


def _stream_local(prompt: str):
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": MODEL_NAME, "prompt": prompt, "stream": True,
                  "options": {"num_predict": 1500, "num_ctx": 3072, "temperature": 0.2}},
            stream=True, timeout=180,
        )
        r.raise_for_status()
        for line in r.iter_lines():
            if line:
                data = json.loads(line)
                if not data.get("done"):
                    yield data.get("response", "")
    except Exception as e:
        yield f"\n[Ollama error: {e}]"


def _stream_gemini(prompt, api_key, model):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent"
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 2048, "temperature": 0.2}}
    r = requests.post(url, json=body, params={"key": api_key, "alt": "sse"}, stream=True, timeout=90)
    r.raise_for_status()
    for line in r.iter_lines():
        if line and line.startswith(b"data: "):
            data_str = line[6:]
            if data_str == b"[DONE]": break
            try:
                d = json.loads(data_str)
                for part in d.get("candidates", [{}])[0].get("content", {}).get("parts", []):
                    yield part.get("text", "")
            except Exception:
                pass


def _stream_claude(prompt, api_key, model):
    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01",
               "content-type": "application/json"}
    body = {"model": model, "max_tokens": 2048, "stream": True,
            "messages": [{"role": "user", "content": prompt}]}
    r = requests.post("https://api.anthropic.com/v1/messages",
                      json=body, headers=headers, stream=True, timeout=90)
    r.raise_for_status()
    for line in r.iter_lines():
        if line and line.startswith(b"data: "):
            try:
                d = json.loads(line[6:])
                if d.get("type") == "content_block_delta":
                    yield d.get("delta", {}).get("text", "")
            except Exception:
                pass


def _stream_openai_compat(prompt, api_key, model, base_url):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {"model": model, "stream": True, "temperature": 0.2, "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}]}
    r = requests.post(f"{base_url}/chat/completions",
                      json=body, headers=headers, stream=True, timeout=90)
    r.raise_for_status()
    for line in r.iter_lines():
        if line and line.startswith(b"data: "):
            data_str = line[6:]
            if data_str == b"[DONE]": break
            try:
                yield json.loads(data_str)["choices"][0]["delta"].get("content", "")
            except Exception:
                pass


def get_stream(query, vectorstore, provider, api_key, ext_model):
    context = ""
    if vectorstore:
        retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
        docs = retriever.invoke(query)
        context = "\n\n---\n\n".join(d.page_content[:400] for d in docs)
    prompt = _TEMPLATE.format(context=context, question=query)

    if provider == "local":
        yield from _stream_local(prompt)
    elif provider == "gemini":
        yield from _stream_gemini(prompt, api_key, ext_model)
    elif provider == "claude":
        yield from _stream_claude(prompt, api_key, ext_model)
    elif provider == "deepseek":
        yield from _stream_openai_compat(prompt, api_key, ext_model, "https://api.deepseek.com")
    elif provider == "openai":
        yield from _stream_openai_compat(prompt, api_key, ext_model, "https://api.openai.com/v1")


# ── RESULT RENDERER ────────────────────────────────────────────────────────

def render_results(r: dict):
    if "_raw" in r:
        st.warning("Could not parse structured JSON — showing raw output.")
        st.code(r["_raw"], language="json")
        return

    # 1. Recommended Architecture
    style     = r.get("recommended_style", "—")
    rationale = r.get("architecture_rationale", "")
    st.markdown(f"""
<div class="panel">
  <div class="panel-label">Recommended Architecture</div>
  <div class="arch-badge">{style}</div>
  <div style="margin-top:0.7rem;">
    <div class="panel-label">Justification</div>
    <div class="just-box">{rationale}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # 2. Requirements + Quality Attributes
    frs  = r.get("functional_requirements", [])
    nfrs = r.get("non_functional_requirements", [])
    qas  = r.get("quality_attributes", [])
    st.markdown(f"""
<div class="panel">
  <div class="panel-label">Functional Requirements</div>
  {tags_html(frs, "tag-green")}
  <div style="margin-top:0.8rem;"><div class="panel-label">Non-Functional Requirements</div>{tags_html(nfrs, "tag-blue")}</div>
  <div style="margin-top:0.8rem;"><div class="panel-label">Quality Attributes</div>{tags_html(qas, "tag-purple")}</div>
</div>""", unsafe_allow_html=True)

    # 3. Architecture Tactics
    sc = r.get("scalability_tactics", [])
    av = r.get("availability_tactics", [])
    se = r.get("security_tactics", [])
    st.markdown(f"""
<div class="panel">
  <div class="panel-label">Scalability Tactics</div>{tags_html(sc, "tag-blue")}
  <div style="margin-top:0.8rem;"><div class="panel-label">Availability Tactics</div>{tags_html(av, "tag-green")}</div>
  <div style="margin-top:0.8rem;"><div class="panel-label">Security Tactics</div>{tags_html(se, "tag-amber")}</div>
</div>""", unsafe_allow_html=True)

    # 4. Components
    comps = r.get("components", [])
    rows = "".join(
        f'<div class="comp-row">'
        f'<span class="comp-name">{c.get("name", "")}</span>'
        f'<span class="comp-role">{c.get("role", "")}</span>'
        f'<span class="comp-tech">{c.get("technology", "")}</span>'
        f'</div>'
        for c in comps
    )
    st.markdown(f"""
<div class="panel">
  <div class="panel-label">Components ({len(comps)})</div>
  {rows}
</div>""", unsafe_allow_html=True)

    # 5. Tech Stack + Deployment
    ts  = r.get("tech_stack", {})
    dep = r.get("deployment_recommendation", "")
    stack_items = "".join(
        f'<div class="stack-item"><div class="stack-layer">{k}</div><div class="stack-value">{v}</div></div>'
        for k, v in ts.items()
    )
    st.markdown(f"""
<div class="panel">
  <div class="panel-label">Tech Stack</div>
  <div class="stack-grid">{stack_items}</div>
  <div style="margin-top:0.85rem;">
    <div class="panel-label">Deployment</div>
    <div class="just-box">&#128640; {dep}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # 6. Risk Assessment
    risks = r.get("risk_assessment", [])
    risk_html = "".join(f'<div class="risk"><span>&#9651;</span><span>{rk}</span></div>' for rk in risks)
    st.markdown(f"""
<div class="panel">
  <div class="panel-label">Risk Assessment</div>
  {risk_html}
</div>""", unsafe_allow_html=True)

    # 7. Architecture Diagram
    raw_diagram   = r.get("mermaid_diagram", "graph TD\n  A --> B")
    raw_diagram   = raw_diagram.replace("\\n", "\n")
    clean_diagram = sanitize_mermaid(raw_diagram)
    live_url      = get_mermaid_live_url(clean_diagram)

    st.markdown(f"""
<div class="panel">
  <div class="panel-label">Architecture Diagram</div>
  <div class="mermaid-code">{clean_diagram}</div>
  <a href="{live_url}" target="_blank" class="live-btn">&#8599; Open in Mermaid Live</a>
</div>""", unsafe_allow_html=True)

    try:
        st_mermaid(clean_diagram, height="520px")
    except Exception as e:
        st.caption(f"Inline render unavailable — use the link above. ({e})")


# ── PAGE SETUP ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Software Engineering Workbench",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

dark = st.session_state.dark_mode
st.markdown(build_css(dark), unsafe_allow_html=True)

# ── HEADER ─────────────────────────────────────────────────────────────────

hdr_l, hdr_r = st.columns([7, 1])
with hdr_l:
    st.markdown(f"""
<div class="wb-shell">
  <div class="wb-header">
    <div class="wb-wordmark">
      <div class="wb-logo">
        <svg viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
          <path d="M10 2L12.7 7.5L19 8.4L14.5 12.8L15.6 19L10 16.2L4.4 19L5.5 12.8L1 8.4L7.3 7.5Z"/>
        </svg>
      </div>
      <div>
        <div class="wb-title">AI-Base Software Engineering Workbench</div>
        <div class="wb-tagline">
          From requirements to architecture — instantly
        </div>
        <div class="wb-sub">INTELLIGENT ARCHITECTURE ASSISTANT &nbsp;·&nbsp; {MODEL_NAME.upper()} &nbsp;·&nbsp; NOMIC EMBEDDINGS</div>
      </div>
    </div>
  </div>
  <hr class="wb-divider">
</div>""", unsafe_allow_html=True)

with hdr_r:
    toggle_label = "☀ Light" if dark else "☽ Dark"
    if st.button(toggle_label, key="wb_theme_btn"):
        st.session_state.dark_mode = not dark
        st.rerun()

# ── KNOWLEDGE BASE ─────────────────────────────────────────────────────────

vectorstore = load_and_process_documents()

if vectorstore is None:
    st.markdown(f"""
<div class="status-chip" style="background:rgba(251,191,36,0.10);border-color:#FBBF24;color:#FBBF24;">
  <span style="width:6px;height:6px;border-radius:50%;background:#FBBF24;display:inline-block;"></span>
  No knowledge base — add files to <code style="font-size:0.65rem;">{PDF_DIRECTORY}/</code>
</div>""", unsafe_allow_html=True)
else:
    st.markdown("""
<div class="status-chip">
  <span class="status-dot"></span>Knowledge base ready
</div>""", unsafe_allow_html=True)

# ── MAIN LAYOUT ─────────────────────────────────────────────────────────────

col_left, col_right = st.columns([1, 1.45], gap="large")

with col_left:

    # Model selector
    st.markdown('<div class="panel"><div class="panel-label">Model Configuration</div>', unsafe_allow_html=True)

    model_options = []
    model_meta = {}
    for provider_key, (provider_label, models) in PROVIDERS.items():
        for model_name in models:
            option_label = f"{provider_label} · {model_name}"
            model_options.append(option_label)
            model_meta[option_label] = (provider_key, model_name)

    m_col1, m_col2 = st.columns([1.2, 1])
    with m_col1:
        selected_option = st.selectbox("Model", model_options, key="wb_model_select")
    with m_col2:
        api_key = st.text_input(
            "API Key", type="password",
            placeholder="Paste key…",
            key="wb_api_key",
        )

    chosen_provider, ext_model = model_meta[selected_option]

    if chosen_provider != "local" and not api_key:
        st.caption("API key required for this model.")
    elif chosen_provider == "local":
        st.caption(f"Using local **{ext_model}** via Ollama — no key needed.")

    st.markdown('</div>', unsafe_allow_html=True)

    # Requirements textarea
    st.markdown('<div class="panel"><div class="panel-label">System Requirements</div>', unsafe_allow_html=True)
    user_req = st.text_area(
        label="req", label_visibility="collapsed", height=200,
        placeholder=(
            "Describe what the system should do…\n\n"
            "e.g. A system that monitors patient vitals in real time via wearables. "
            "Doctors are alerted for anomalies and patient history is stored securely."
        ),
        key="wb_user_req",
    )
    ready    = chosen_provider == "local" or bool(api_key)
    generate = st.button(
        f"Generate  ·  {PROVIDERS[chosen_provider][0]}",
        key="wb_gen_btn", disabled=not ready,
    )
    if not ready:
        st.caption("Enter an API key above to enable generation.")

    st.markdown('</div>', unsafe_allow_html=True)

    # Tips
    tips = [
        "Mention expected user load or data volume",
        "Include compliance needs (HIPAA, GDPR, PCI-DSS)",
        "Specify real-time vs batch requirements",
        "List external integrations (APIs, devices, third-parties)",
    ]
    tip_items = "".join(
        f'<div class="tip-item"><span class="tip-bullet"></span><span>{t}</span></div>'
        for t in tips
    )
    st.markdown(f"""
<div class="panel">
  <div class="panel-label">Tips for better results</div>
  {tip_items}
</div>""", unsafe_allow_html=True)


with col_right:

    if generate:
        if not user_req.strip():
            st.warning("Please enter some requirements first.")
        else:
            prov_label  = PROVIDERS[chosen_provider][0]
            model_label = ext_model if chosen_provider != "local" else MODEL_NAME
            try:
                with st.status(f"Generating with {prov_label} / {model_label}…",
                               expanded=True) as gen_status:
                    raw_text = st.write_stream(
                        get_stream(user_req, vectorstore, chosen_provider, api_key, ext_model)
                    )
                    gen_status.update(label=f"Done — {prov_label}", state="complete",
                                      expanded=False)
                result = _parse_json(raw_text)
                st.session_state["arch_result"]   = result
                st.session_state["arch_provider"]  = prov_label
                st.session_state["arch_raw"]       = raw_text
            except requests.HTTPError as e:
                st.error(f"API error {e.response.status_code}: {e.response.text[:300]}")
            except Exception as e:
                st.error(f"{type(e).__name__}: {e}")

    if "arch_result" in st.session_state:
        prov = st.session_state.get("arch_provider", "")
        st.markdown(f"""
<div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.65rem;">
  <span style="font-family:'IBM Plex Mono',monospace;font-size:0.63rem;letter-spacing:0.1em;text-transform:uppercase;">Result</span>
  <span style="background:var(--surface2,#191D28);border:1px solid var(--border,#252B3B);border-radius:100px;padding:0.1rem 0.6rem;font-size:0.65rem;font-family:'IBM Plex Mono',monospace;">{prov}</span>
</div>""", unsafe_allow_html=True)

        render_results(st.session_state["arch_result"])

        with st.expander("Raw LLM output"):
            st.code(st.session_state.get("arch_raw", ""), language="json")

    else:
        st.markdown("""
<div class="empty-state">
  <div class="empty-icon">
    <svg viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
  </div>
  <div class="empty-title">Ready to design</div>
  <div class="empty-sub">Select a provider, describe your system,<br>then click <strong>Generate</strong></div>
</div>""", unsafe_allow_html=True)
