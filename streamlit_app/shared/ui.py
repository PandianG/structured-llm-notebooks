"""Shared Streamlit UI helpers: sidebar, cached clients, consistent styling."""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # allow `src` imports

import src.config as config  # noqa: E402

ACCENT = "#7c6cf5"
ACCENT_SOFT = "rgba(124, 108, 245, 0.12)"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"], .stMarkdown, .stText, p, li, label, .stSelectbox, .stSlider {
    font-family: 'Inter', -apple-system, sans-serif;
}

h1, h2, h3, h4, .sidebar-title {
    font-family: 'Sora', 'Inter', sans-serif !important;
    letter-spacing: -0.02em;
}

h1 { font-weight: 800; }
h2, h3 { font-weight: 700; }

code, pre, [data-testid="stCodeBlock"] {
    font-family: 'JetBrains Mono', monospace !important;
}

/* ---- buttons ---------------------------------------------------------- */
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    transition: all .15s ease;
    border: 1px solid rgba(128,128,128,.25);
}
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(0,0,0,.25); }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7c6cf5 0%, #5a8dee 100%);
    border: none;
    color: white;
}

/* ---- metrics ------------------------------------------------------------ */
[data-testid="stMetric"] {
    background: rgba(128,128,128,.07);
    border: 1px solid rgba(128,128,128,.12);
    border-radius: 14px;
    padding: 14px 18px;
}
[data-testid="stMetricLabel"] { font-family: 'Inter', sans-serif; font-weight: 600; }
[data-testid="stMetricValue"] { font-family: 'Sora', sans-serif; font-weight: 700; }

/* ---- expanders ---------------------------------------------------------- */
[data-testid="stExpander"] {
    border: 1px solid rgba(128,128,128,.15);
    border-radius: 12px;
}
[data-testid="stExpander"] summary { font-weight: 600; font-family: 'Inter', sans-serif; }

/* ---- text inputs / text areas ------------------------------------------- */
.stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
    border-radius: 10px !important;
}

/* ---- sidebar ------------------------------------------------------------ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(124,108,245,.08) 0%, rgba(0,0,0,0) 40%);
}
section[data-testid="stSidebar"] hr {
    margin: 0.8em 0;
    border-color: rgba(128,128,128,.15);
}

/* ---- custom building blocks --------------------------------------------- */
.lab-card {
    background: rgba(128,128,128,.07);
    border: 1px solid rgba(128,128,128,.14);
    border-radius: 14px;
    padding: 14px 16px;
    margin: 6px 0;
}
.lab-card .lab-card-label {
    font-size: .72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .08em;
    opacity: .55;
    margin-bottom: 4px;
}
.lab-card .lab-card-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: .86rem;
    font-weight: 600;
}
.pill {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: .78rem;
    font-weight: 600;
    margin: 2px 4px 2px 0;
}
.pill-ok   { background: rgba(46,204,113,.15); color: #2ecc71; }
.pill-bad  { background: rgba(231,76,60,.15);  color: #e74c3c; }
.pill-info { background: rgba(124,108,245,.16); color: #9d8ffb; }
.sidebar-heading {
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 1.05rem;
    margin: 4px 0 2px 0;
}
.sidebar-sub {
    font-size: .8rem;
    opacity: .6;
    margin-bottom: 10px;
}
.lab-explain {
    border-left: 4px solid #7c6cf5;
    background: rgba(124,108,245,.10);
    border-radius: 0 12px 12px 0;
    padding: 12px 16px;
    margin: 8px 0;
}
.lab-explain .lab-explain-title {
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: .92rem;
    margin-bottom: 4px;
}
.lab-explain .lab-explain-body {
    font-size: .92rem;
    line-height: 1.55;
}
.lab-try {
    font-size: .85rem;
    opacity: .75;
    margin: 2px 0 12px 0;
}
"""


def inject_css() -> None:
    """Apply the lab's visual theme. Call once per page, after set_page_config."""
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Cached clients — built once per session
# ---------------------------------------------------------------------------
@st.cache_resource
def get_openai_client():
    return config.get_openai_client()


@st.cache_resource
def get_instructor(provider: str):
    return config.get_instructor_client(provider)


@st.cache_resource
def get_outlines_model():
    import outlines

    return outlines.from_openai(get_openai_client(), config.get_openai_model())


@st.cache_resource
def get_outlines_local_model(model_name: str = "Qwen/Qwen2.5-0.5B-Instruct"):
    """Outlines with a local transformers model — required for regex/CFG constraints,
    which need token-level masking (not available through the OpenAI API)."""
    import outlines
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    hf_model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.float32)
    return outlines.from_transformers(hf_model, tokenizer)


# ---------------------------------------------------------------------------
# Page chrome
# ---------------------------------------------------------------------------
def render_sidebar() -> dict:
    """Polished sidebar: model cards, key pills, intuitive sliders. Returns settings."""
    sb = st.sidebar

    sb.markdown(
        '<div class="sidebar-heading">🧪 Lab Settings</div>'
        '<div class="sidebar-sub">Tune the demos — changes apply on the next run.</div>',
        unsafe_allow_html=True,
    )

    # --- environment cards ---
    openai_set = bool(config.OPENAI_API_KEY)
    anthropic_set = bool(config.ANTHROPIC_API_KEY)
    sb.markdown(
        f'<div class="lab-card">'
        f'<div class="lab-card-label">OpenAI model</div>'
        f'<div class="lab-card-value">{config.get_openai_model()}</div>'
        f'<div style="margin-top:8px">'
        f'<span class="pill {"pill-ok" if openai_set else "pill-bad"}">'
        f"{'● key connected' if openai_set else '○ key missing'}</span>"
        f"</div></div>",
        unsafe_allow_html=True,
    )
    sb.markdown(
        f'<div class="lab-card">'
        f'<div class="lab-card-label">Anthropic model</div>'
        f'<div class="lab-card-value">{config.get_anthropic_model()}</div>'
        f'<div style="margin-top:8px">'
        f'<span class="pill {"pill-ok" if anthropic_set else "pill-bad"}">'
        f"{'● key connected' if anthropic_set else '○ key missing'}</span>"
        f"</div></div>",
        unsafe_allow_html=True,
    )

    mode_pills = []
    if config.USE_OLLAMA:
        mode_pills.append('<span class="pill pill-info">local · Ollama</span>')
    if config.USE_SMALL_MODEL:
        mode_pills.append('<span class="pill pill-info">cost-saving · mini models</span>')
    if not mode_pills:
        mode_pills.append('<span class="pill pill-info">full-size models</span>')
    sb.markdown(
        '<div class="lab-card"><div class="lab-card-label">Runtime mode</div>'
        + "".join(mode_pills)
        + "</div>",
        unsafe_allow_html=True,
    )

    sb.markdown("---")

    # --- controls with helper captions ---
    sample_size = sb.slider("Benchmark sample size", 3, 25, 8)
    sb.caption("How many real dataset rows each benchmark processes.")
    temperature = sb.slider("Temperature — raw demos only", 0.0, 1.0, 0.7, 0.1)
    sb.caption("Instructor & Outlines demos always use their own safe settings.")

    return {"sample_size": sample_size, "temperature": temperature}


def section(title: str, body: str) -> None:
    st.markdown(f"### {title}\n\n{body}")


def explain(title: str, body: str) -> None:
    """'What's happening' callout — the teaching moment attached to every demo."""
    st.markdown(
        f'<div class="lab-explain"><div class="lab-explain-title">💡 {title}</div>'
        f'<div class="lab-explain-body">{body}</div></div>',
        unsafe_allow_html=True,
    )


def try_this(body: str) -> None:
    """Small student prompt under a demo."""
    st.markdown(f'<div class="lab-try">👉 <b>Try this:</b> {body}</div>', unsafe_allow_html=True)


def show_code(title: str, code: str) -> None:
    with st.expander(f"🐍 {title}"):
        st.code(code, language="python")


def api_error(e: Exception) -> None:
    """Friendly error panel so students never hit a raw stack trace."""
    st.error(f"**API call failed:** `{type(e).__name__}: {e}`")
    st.info("Check your API keys in `.env`, or set USE_OLLAMA=true for local models.")
