"""Page 1 — Without Instructor: raw prompting and its failure modes."""

import json
import sys
import traceback
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # allow `shared` imports

from shared import data, models, prompts, ui  # noqa: E402

import src.config as config  # noqa: E402

st.set_page_config(page_title="1 · Without Instructor", page_icon="❌", layout="wide")
ui.inject_css()

st.title("❌ Without Instructor: raw prompting")
st.markdown(
    """
This is what a naive integration looks like: *"I'll just ask the model to return JSON
and parse it."* Watch what actually comes back.
"""
)

settings = ui.render_sidebar()
client = ui.get_openai_client()
model_name = config.get_model()

# ---------------------------------------------------------------------------
# Demo A — one-shot raw extraction
# ---------------------------------------------------------------------------
ui.section(
    "Demo A — one raw call, then try to parse it",
    "Pick (or type) some text, send it to the model with nothing but a polite schema hint, "
    "then watch Python try — and often fail — to parse the reply.",
)

preset = st.selectbox(
    "Input preset",
    ["Person", "Invoice", "Custom"],
    help="Invoice uses a real document from data/invoices.jsonl",
)

if preset == "Person":
    default_text = "Alice, 30, lives in New York"
    hint = prompts.PERSON_SCHEMA_HINT
elif preset == "Invoice":
    sample_invoice = data.load_invoices(1)[0]
    default_text = sample_invoice["raw_text"]
    hint = prompts.INVOICE_SCHEMA_HINT
else:
    default_text = "Bob is 25 and from San Francisco"
    hint = prompts.PERSON_SCHEMA_HINT

text = st.text_area("Text to extract from", value=default_text, height=100)

if st.button("🚀 Ask raw", type="primary"):
    messages = prompts.raw_extract_prompt(hint, text)
    ui.show_code(
        "The exact code that runs",
        f"""messages = [
    {{"role": "system", "content": {hint!r}}},
    {{"role": "user", "content": f"Extract: {{text}}"}},
]
response = client.chat.completions.create(
    model={model_name!r},
    messages=messages,
    temperature={settings["temperature"]},
)
raw = response.choices[0].message.content   # <-- this is just a str!
""",
    )
    try:
        with st.spinner("Calling the model…"):
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=settings["temperature"],
            )
        raw = response.choices[0].message.content
    except Exception as e:  # noqa: BLE001
        ui.api_error(e)
        st.stop()

    col_out, col_parse = st.columns(2)
    with col_out:
        st.markdown("**What the model returned (a plain string):**")
        st.code(raw, language=None)

    with col_parse:
        st.markdown("**Your code now has to parse it:**")
        try:
            parsed = json.loads(raw)
            st.success(f"`json.loads` succeeded — but what type is each value? `{parsed}`")
            st.warning(
                "Even when parsing works, fields can be renamed, retyped "
                "(age as string!), or missing — nothing checks that."
            )
        except json.JSONDecodeError as e:
            st.error(f"`json.loads` raised **JSONDecodeError: {e}**")
            with st.expander("Show the traceback your users would never see"):
                try:
                    json.loads(raw)
                except json.JSONDecodeError:
                    st.code(traceback.format_exc(), language="python")

# ---------------------------------------------------------------------------
# Demo B — failure-mode gallery
# ---------------------------------------------------------------------------
ui.section(
    "Demo B — the failure-mode gallery",
    "Real-world shapes of raw output that break `json.loads` or silently corrupt data. "
    "All of these came from *the same prompt style* you just ran.",
)

gallery = [
    (
        "Markdown fences",
        '```json\n{"name": "Alice", "age": 30, "city": "New York"}\n```',
        "The model loves fences. `json.loads` dies on the first backtick.",
    ),
    (
        "Helpful commentary",
        'Sure! Here is the extracted information:\n{"name": "Alice", "age": 30, "city": "New York"}\nHope this helps!',
        "Prose wrapped around the JSON — you now need regex surgery to extract it.",
    ),
    (
        "Renamed keys",
        '{"full_name": "Alice", "years_old": 30, "location": "New York"}',
        "Parses fine, but your code reads `name` and gets KeyError — or worse, None.",
    ),
    (
        "Wrong types",
        '{"name": "Alice", "age": "30", "city": "New York"}',
        "Parses fine too, but `age` is a string. Sorting or math on it crashes later.",
    ),
    (
        "Truncation",
        '{"name": "Alice", "age": 30, "city": "New',
        "Hit max_tokens mid-JSON. Every parse fails and the call is wasted.",
    ),
]
for name, sample, why in gallery:
    with st.expander(f"💥 {name}"):
        st.code(sample, language=None)
        st.markdown(f"**What went wrong:** {why}")

# ---------------------------------------------------------------------------
# Demo C — adherence benchmark
# ---------------------------------------------------------------------------
ui.section(
    "Demo C — adherence benchmark: how often does raw prompting actually work?",
    "We run **N invoices** from `data/invoices.jsonl` through the raw prompt. For each "
    "response we check: (1) does `json.loads` succeed? (2) does the result validate "
    "against the `Invoice` Pydantic model? At temperature 0.7 you will rarely see 100%.",
)

if st.button("🏁 Run raw benchmark", type="primary"):
    rows = data.load_invoices(settings["sample_size"])
    results = []
    progress = st.progress(0, text="Running raw extractions…")
    for i, row in enumerate(rows):
        try:
            resp = client.chat.completions.create(
                model=model_name,
                messages=prompts.raw_extract_prompt(prompts.INVOICE_SCHEMA_HINT, row["raw_text"]),
                temperature=settings["temperature"],
            )
            raw = resp.choices[0].message.content
        except Exception as e:  # noqa: BLE001
            ui.api_error(e)
            st.stop()

        valid_json, schema_valid = False, False
        parsed = None
        try:
            parsed = json.loads(raw)
            valid_json = True
            models.Invoice.model_validate(parsed)
            schema_valid = True
        except (json.JSONDecodeError, ValueError):
            pass
        results.append(
            {
                "id": i,
                "valid JSON": valid_json,
                "schema-valid": schema_valid,
                "raw output (truncated)": (raw or "")[:120],
            }
        )
        progress.progress((i + 1) / len(rows), text=f"{i + 1}/{len(rows)} done")

    df = pd.DataFrame(results)
    c1, c2, c3 = st.columns(3)
    c1.metric("Valid JSON", f"{df['valid JSON'].mean() * 100:.0f}%")
    c2.metric("Schema-valid (Invoice)", f"{df['schema-valid'].mean() * 100:.0f}%")
    c3.metric("N", len(df))

    st.bar_chart(
        pd.DataFrame(
            {
                "stage": ["valid JSON", "schema-valid"],
                "percent": [df["valid JSON"].mean() * 100, df["schema-valid"].mean() * 100],
            }
        ).set_index("stage")
    )

    st.markdown("**Failures (these are the invoices your pipeline silently drops):**")
    st.dataframe(df[~df["schema-valid"]], width="stretch")

    st.session_state["raw_invoice_adherence"] = df["schema-valid"].mean() * 100
    st.info(
        "Keep this number in mind — Page 2 (Instructor) and Page 4 (Outlines) rerun the "
        "exact same benchmark with a structured-output library."
    )

ui.show_code(
    "Scoring logic (nothing fancy — that's the point)",
    """try:
    parsed = json.loads(raw)              # stage 1: is it JSON at all?
    Invoice.model_validate(parsed)        # stage 2: does it match the schema?
    schema_valid = True
except (json.JSONDecodeError, ValueError):
    schema_valid = False""",
)
