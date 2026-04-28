import streamlit as st
import requests
import re
import html
import streamlit.components.v1 as components

# --- CONFIGURATION ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3" # Make sure you have pulled this model via Ollama

THEME_CSS = """
<style>
:root {
  --background: #f7f7f4;
  --surface: #ffffff;
  --surface-muted: #f8fafc;

  --text-primary: #111827;
  --text-secondary: #475569;
  --text-muted: #64748b;

  --border: #e5e7eb;
  --border-strong: #d1d5db;

  --primary: #4f46e5;
  --primary-hover: #4338ca;
  --primary-soft: #eef2ff;

  --success-soft: #ecfdf5;
  --warning-soft: #fffbeb;
  --danger-soft: #fff1f2;
}

.stApp {
  background: var(--background);
  color: var(--text-primary);
}

.block-container {
  max-width: 1440px;
  margin: 0 auto;
  padding-top: 1.8rem;
  padding-bottom: 2.4rem;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.8rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--primary);
  color: #ffffff;
  display: grid;
  place-items: center;
  box-shadow: 0 8px 18px rgba(79, 70, 229, 0.25);
  font-weight: 700;
}

.brand-title {
  font-size: 22px;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
}

.brand-subtitle {
  font-size: 12px;
  color: var(--text-muted);
  margin: 2px 0 0 0;
}

[data-testid="stVerticalBlockBorderWrapper"] > div {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04), 0 8px 24px rgba(15, 23, 42, 0.06);
  padding: 16px;
}

[data-testid="column"]:first-child [data-testid="stVerticalBlock"] {
  position: sticky;
  top: 1.2rem;
}

.section-title {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-secondary);
  margin-bottom: 10px;
}

.section-heading {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.recommendation-card {
  border-left: 4px solid var(--primary);
  background: linear-gradient(180deg, #ffffff 0%, #f8f9ff 100%);
  border-radius: 14px;
  padding: 14px;
  margin-bottom: 16px;
}

.architecture-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
  background: var(--primary-soft);
  color: #3730a3;
  border: 1px solid #c7d2fe;
  font-size: 13px;
  font-weight: 600;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  line-height: 1;
  border: 1px solid transparent;
  margin: 4px 6px 2px 0;
}

.chip-blue { background: #eff6ff; color: #1d4ed8; border-color: #bfdbfe; }
.chip-green { background: #ecfdf5; color: #047857; border-color: #a7f3d0; }
.chip-yellow { background: #fffbeb; color: #92400e; border-color: #fde68a; }
.chip-purple { background: #f5f3ff; color: #6d28d9; border-color: #ddd6fe; }

.risk-list { display: grid; gap: 10px; }

.risk-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  border-radius: 12px;
  background: #fff1f2;
  border: 1px solid #fecdd3;
  color: #9f1239;
  padding: 12px 14px;
  font-size: 14px;
}

.diagram-preview {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 12px;
  min-height: 360px;
  overflow: auto;
}

.diagram-code {
  background: #0f172a;
  color: #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  font-size: 13px;
  overflow-x: auto;
}

div[data-testid="stButton"] button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: none;
  border-radius: 12px;
  background: var(--primary);
  color: #ffffff;
  padding: 11px 18px;
  font-size: 14px;
  font-weight: 700;
  box-shadow: 0 8px 18px rgba(79, 70, 229, 0.24);
  transition: transform 160ms ease, box-shadow 160ms ease, background 160ms ease;
}

div[data-testid="stButton"] button:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(79, 70, 229, 0.28);
}

div[data-testid="stTextArea"] textarea,
div[data-baseweb="select"] > div,
input {
  border: 1px solid var(--border-strong) !important;
  border-radius: 12px !important;
  background: #ffffff !important;
  color: #111827 !important;
}

div[data-testid="stTextArea"] textarea:focus {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.12) !important;
}
</style>
"""

def generate_architecture(requirements):
    """Sends the user requirements to the local LLM and streams the response."""
    
    # This system prompt enforces the rules of Software Architecture based on your course material
    prompt = f"""
    You are an Expert Software Architect. Your job is to read high-level user requirements and propose a robust solution architecture.
    
    When designing the architecture, consider the following concepts:
    - Architectural Styles: Service-Oriented Architecture (SOA), Microservices, Layered, Event-Driven.
    - Scalability Tactics: Vertical scaling, Vertical partitioning, Horizontal scaling, Data partitioning/Sharding, Caching.
    - Availability Tactics: Active redundancy, Heartbeat, Transaction (ACID), Checkpoint/Rollback.
    
    User Requirements:
    {requirements}
    
    Please provide your output structured with the following sections:
    1. Stakeholders & Quality Attributes
    2. Architecture at Large (Macro Level) - Suggested styles and why.
    3. Architecture at Small (Micro Level) - Internal component structure.
    4. Key Tactics applied (Availability, Performance, Scalability).
    """

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        return f"Error connecting to local model: {e}. Is Ollama running?"


def split_sections(proposal_text):
    pattern = re.compile(r"^\s*(\d+)[\.)]\s*(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(proposal_text))
    if not matches:
        return {"full": proposal_text.strip()}

    sections = {}
    for i, match in enumerate(matches):
        title = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(proposal_text)
        body = proposal_text[start:end].strip()
        sections[title] = body
    return sections


def extract_mermaid_code(text):
    match = re.search(r"```mermaid\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def render_mermaid(mermaid_code):
    safe_mermaid = html.escape(mermaid_code)
    html_content = f"""
    <div class="diagram-preview">
      <pre class="mermaid">{safe_mermaid}</pre>
    </div>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
      mermaid.initialize({{
        startOnLoad: true,
        theme: "base",
        themeVariables: {{
          background: "#ffffff",
          primaryColor: "#eef2ff",
          primaryTextColor: "#111827",
          primaryBorderColor: "#6366f1",
          lineColor: "#64748b",
          secondaryColor: "#f8fafc",
          tertiaryColor: "#ffffff",
          fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif"
        }}
      }});
    </script>
    """
    components.html(html_content, height=420, scrolling=True)


def render_chips(values, variant):
    chips = "".join([f'<span class="chip {variant}">{html.escape(v)}</span>' for v in values])
    st.markdown(chips or f'<span class="chip {variant}">No items extracted</span>', unsafe_allow_html=True)


def fallback_mermaid(recommendation):
    label = recommendation if recommendation else "Recommended Architecture"
    label = re.sub(r"[^a-zA-Z0-9\s-]", "", label)[:45]
    return f"""flowchart LR
Client[Users / Clients] --> Gateway[API Gateway]
Gateway --> ServiceA[{label}]
ServiceA --> DB[(Primary Data Store)]
ServiceA --> Cache[(Cache)]
"""

# --- UI BUILDER (STREAMLIT) ---
st.set_page_config(page_title="Software Architecture Workbench", layout="wide")
st.markdown(THEME_CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="app-header">
      <div class="brand">
        <div class="brand-icon">🏗</div>
        <div>
          <h1 class="brand-title">Software Architecture Workbench</h1>
          <p class="brand-subtitle">Powered by Local AI (Ollama). No API quotas required.</p>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

left_col, right_col = st.columns([0.95, 1.65], gap="large")

with left_col:
    with st.container(border=True):
        st.markdown('<div class="section-title">Configuration</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">Enter System Requirements</div>', unsafe_allow_html=True)
        user_requirements = st.text_area(
            "Describe what the system needs to do, the expected user load, and any constraints:",
            height=220,
            placeholder="e.g., Build an e-commerce platform that can handle 10,000 concurrent users during flash sales...",
            label_visibility="collapsed",
        )
        generate_click = st.button("Generate Solution Architecture", use_container_width=True)

with right_col:
    with st.container(border=True):
        st.markdown('<div class="section-title">Generated Output</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">Architecture Recommendation</div>', unsafe_allow_html=True)

if generate_click:
    if not user_requirements.strip():
        st.warning("Please enter some requirements first.")
    else:
        with st.spinner("Analyzing requirements and designing architecture..."):
            architecture_proposal = generate_architecture(user_requirements)

        sections = split_sections(architecture_proposal)
        architecture_text = sections.get("Architecture at Large (Macro Level) - Suggested styles and why.", "")
        micro_text = sections.get("Architecture at Small (Micro Level) - Internal component structure.", "")
        tactics_text = sections.get("Key Tactics applied (Availability, Performance, Scalability).", "")
        stakeholders_text = sections.get("Stakeholders & Quality Attributes", "")
        recommendation = architecture_text.split("\n")[0].strip("- ") if architecture_text else "Recommended architecture generated"

        tactics_candidates = re.findall(
            r"Microservices|SOA|Layered|Event-Driven|Caching|Sharding|Horizontal scaling|Vertical scaling|Active redundancy|Checkpoint/Rollback|ACID",
            architecture_proposal,
            flags=re.IGNORECASE,
        )
        normalized_tactics = sorted(set([t.title() for t in tactics_candidates]))

        risk_lines = []
        for line in architecture_proposal.splitlines():
            if re.search(r"risk|trade-off|challenge|constraint", line, re.IGNORECASE):
                risk_lines.append(line.strip("-• "))

        mermaid_code = extract_mermaid_code(architecture_proposal)
        if not mermaid_code:
            mermaid_code = fallback_mermaid(recommendation)

        with right_col:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div class="recommendation-card">
                      <div class="section-title">Recommended Architecture</div>
                      <span class="architecture-badge">⭐ {html.escape(recommendation)}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown('<div class="section-title">Stakeholders & Quality Attributes</div>', unsafe_allow_html=True)
                st.markdown(stakeholders_text or "No explicit stakeholder section returned.")

                st.markdown('<div class="section-title">Architecture (Macro / Micro)</div>', unsafe_allow_html=True)
                st.markdown(architecture_text or "No macro-level details returned.")
                if micro_text:
                    st.markdown(micro_text)

                st.markdown('<div class="section-title">Key Tactics</div>', unsafe_allow_html=True)
                render_chips(normalized_tactics, "chip-purple")
                if tactics_text:
                    st.markdown(tactics_text)

                st.markdown('<div class="section-title">Risk Assessment</div>', unsafe_allow_html=True)
                if risk_lines:
                    risk_markup = "".join(
                        [
                            f'<div class="risk-item"><span class="risk-icon">⚠️</span><span>{html.escape(r)}</span></div>'
                            for r in risk_lines[:6]
                        ]
                    )
                    st.markdown(f'<div class="risk-list">{risk_markup}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(
                        '<div class="risk-item"><span class="risk-icon">ℹ️</span><span>No explicit risks were identified by the model. Review assumptions and constraints.</span></div>',
                        unsafe_allow_html=True,
                    )

            with st.container(border=True):
                st.markdown('<div class="section-title">Architecture Diagram (Mermaid)</div>', unsafe_allow_html=True)
                render_mermaid(mermaid_code)

                st.markdown('<div class="section-title">Mermaid Source</div>', unsafe_allow_html=True)
                st.markdown(f"<pre class='diagram-code'>{html.escape(mermaid_code)}</pre>", unsafe_allow_html=True)
