"""Structured LLM Lab — home page.

Run with:  uv run streamlit run streamlit_app/Home.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # allow `shared` imports

import streamlit as st
from shared import ui  # noqa: E402  (importing shared puts the repo root on sys.path)

import src.config as config  # noqa: E402

st.set_page_config(page_title="Structured LLM Lab", page_icon="🧪", layout="wide")
ui.inject_css()

st.title("🧪 Structured LLM Lab")
st.markdown(
    """
Welcome! This app lets you **run live demos** that answer one question:

> *When an LLM must return structured data (JSON, enums, valid code) — what happens
> with a plain API call, and what changes when you add Instructor or Outlines?*

Use the sidebar pages, in order. Each page is hands-on: press the buttons, break things,
change the temperature, and watch what survives.
"""
)

ui.section(
    "The four quadrants — and beyond",
    """
| | **Prompting only** | **With a structured-output library** | **Beyond the basics** |
|---|---|---|---|
| **OpenAI-style chat API** | ❌ Page 1 — *Without Instructor*: pretty-printed prose, JSON that sometimes parses | ✅ Page 2 — *With Instructor*: validated, typed Pydantic objects, auto-retry | 🚀 Page 3 — lists, `Maybe`, raw completions, **modes** |
| **Constrained generation** | ❌ Page 4 — *Without Outlines*: regex/enums/code the model *mostly* gets right | ✅ Page 5 — *With Outlines*: token-level guarantees — invalid output is impossible | 🚀 Page 6 — format types, regex DSL, batching, **grammars** |

Page 7 puts all three working pipelines **head-to-head on the same input**.
""",
)

ui.section(
    "Your environment",
    f"""
- Active provider (`LLM_PROVIDER`): `{config.get_active_provider()}`
- OpenAI model: `{config.get_openai_model()}`
- Anthropic model: `{config.get_anthropic_model()}`
- Gemini model: `{config.get_gemini_model()}` (free tier)
- Groq model: `{config.get_groq_model()}` (free tier)
- Ollama mode: `{config.USE_OLLAMA}`

Every demo calls a real model. Keep **USE_SMALL_MODEL=true** in your `.env` for cheap runs,
or set **LLM_PROVIDER=gemini** / **LLM_PROVIDER=groq** to use a free API tier.
""",
)

ui.render_sidebar()

try:
    import contextlib
    import io

    from src.cost_tracker import print_cost_warning

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print_cost_warning("streamlit_app")
    st.caption(buf.getvalue())
except Exception:  # pragma: no cover - cost tracker is best-effort
    st.caption("💡 Demos call paid APIs — keep N small and USE_SMALL_MODEL=true.")

st.info(
    "**Navigation:** the sidebar pages (1❌ → 2✅ → 3🚀 → 4❌ → 5✅ → 6🚀 → 7⚖️) are "
    "designed to be run in order — pages 4 and 5 share one benchmark story, and the "
    "🚀 pages deepen each library with features the notebooks don't cover."
)
