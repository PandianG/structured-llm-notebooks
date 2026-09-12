"""Page 4 — With Outlines: guaranteed-valid generation."""

import ast
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # allow `shared` imports

from shared import data, models, prompts, ui  # noqa: E402

st.set_page_config(page_title="4 · With Outlines", page_icon="✅", layout="wide")
ui.inject_css()

st.title("✅ With Outlines: make invalid output impossible")
st.markdown(
    """
Outlines constrains generation at the **token level** — the model literally cannot emit
a token that would break the schema, regex, or grammar. No retries needed: the guarantee
is structural, not statistical.
"""
)

settings = ui.render_sidebar()
model = ui.get_outlines_model()

# ---------------------------------------------------------------------------
# Demo A — benchmarks rerun with Outlines (JSON constraints via OpenAI backend)
# ---------------------------------------------------------------------------
ui.section(
    "Demo A — rerun Page 3's benchmarks",
    "Same dataset, same base model — but generation is forced to conform to the "
    "`SentimentResult` schema (a `Literal` = an enum in JSON Schema). Watch the match rates.",
)

if st.button("🏁 Run Outlines benchmark", type="primary"):
    rows = data.load_sentiments(settings["sample_size"])
    labels, correct = [], 0
    progress = st.progress(0, text="Classifying with schema-constrained generation…")
    for i, row in enumerate(rows):
        try:
            raw = model(
                f"{prompts.SENTIMENT_SYSTEM}\n\nText: {row['text']}",
                models.SentimentResult,
            )
            # The OpenAI backend returns the constrained JSON as a string —
            # validation is still guaranteed, parsing is one line.
            label = models.SentimentResult.model_validate_json(raw).label
        except Exception as e:  # noqa: BLE001
            ui.api_error(e)
            st.stop()
        labels.append(label)
        correct += label == row["expected_label"]
        progress.progress((i + 1) / len(rows), text=f"{i + 1}/{len(rows)} done")

    counts = Counter(labels)
    st.bar_chart(
        pd.DataFrame({"label": list(counts), "count": list(counts.values())}).set_index("label")
    )
    c1, c2 = st.columns(2)
    c1.metric("Canonical-label match", f"{len(labels)}/{len(labels)}", delta="forced by schema")
    c2.metric("Correct vs ground truth", f"{correct}/{len(labels)}")

    if "raw_sentiment_adherence" in st.session_state:
        raw_pct = st.session_state["raw_sentiment_adherence"]
        st.success(
            f"Raw prompting matched the contract {raw_pct:.0f}% of the time (your Page 3 run); "
            "Outlines matches it 100% — by construction."
        )
    else:
        st.info("Run Page 3's Demo B first to compare against raw prompting on your own numbers.")

ui.show_code(
    "The exact code that runs",
    """raw = model(text, SentimentResult)  # SentimentResult.label is a Literal
label = SentimentResult.model_validate_json(raw).label
# label is guaranteed to be one of: "positive" | "negative" | "neutral\"""",
)

# ---------------------------------------------------------------------------
# Demo B & C — regex and CFG (local model — token masking can't go through an API)
# ---------------------------------------------------------------------------
st.divider()
ui.section(
    "⚠️ Why these demos use a local model",
    "True token-level masking (regex, grammars) needs control over the logits — something "
    "a hosted API does not expose. Outlines therefore runs a **local transformers model** "
    "here. First run downloads ~1 GB (cached afterwards). This limitation is itself the "
    "lesson: hard guarantees require owning the inference loop.",
)

local_model_name = st.text_input(
    "Local model (Hugging Face id)",
    value="Qwen/Qwen2.5-0.5B-Instruct",
    help="Any small instruct model works, e.g. Qwen2.5-0.5B-Instruct",
)

# ---------------------------------------------------------------------------
# Demo B — regex generation
# ---------------------------------------------------------------------------
ui.section(
    "Demo B — regex-constrained generation",
    "Every emitted token must match the pattern. Edit the regex and sample — **zero** "
    "post-validation code needed.",
)

user_regex = st.text_input("Regex", value=r"\d{3}-\d{4}")
n_regex = st.slider("Samples", 3, 8, 4, key="regex_n")

if st.button("📞 Generate with Outlines"):
    from outlines.types import Regex

    with st.spinner("Loading local model (first run downloads ~1 GB)…"):
        try:
            local_model = ui.get_outlines_local_model(local_model_name)
        except Exception as e:  # noqa: BLE001
            ui.api_error(e)
            st.stop()

    pattern = re.compile(f"^(?:{user_regex})$")
    outputs = []
    with st.spinner("Sampling on CPU…"):
        for i in range(n_regex):
            try:
                out = local_model(
                    f"Generate sample #{i + 1} matching the required format.",
                    Regex(user_regex),
                )
            except Exception as e:  # noqa: BLE001
                ui.api_error(e)
                st.stop()
            outputs.append({"output": out, "matches": bool(pattern.match(out))})

    df = pd.DataFrame(outputs)
    st.dataframe(df, width="stretch")
    st.metric("Match rate", f"{df['matches'].sum()}/{len(df)}", delta="guaranteed")

# ---------------------------------------------------------------------------
# Demo C — CFG playground
# ---------------------------------------------------------------------------
ui.section(
    "Demo C — context-free grammars: always-parseable code",
    "A grammar defines the whole language of valid outputs. Outlines generates only "
    "strings the grammar accepts — then we *prove* it by parsing.",
)

grammar_choice = st.selectbox("Grammar", ["Arithmetic expressions", "SQL SELECT"])
user_prompt = st.text_input("Prompt", value="Write an expression for compound interest")

ARITHMETIC_GRAMMAR = r"""
    start: expr
    expr: expr "+" term
        | expr "-" term
        | term
    term: term "*" factor
        | term "/" factor
        | factor
    factor: NUMBER
          | "(" expr ")"
    NUMBER: /[0-9]+(\.[0-9]+)?/
"""

SQL_GRAMMAR = r"""
    start: select_stmt
    select_stmt: "SELECT" column_list "FROM" table_name where_clause?
    column_list: column_name ("," column_name)*
    column_name: /[a-z_][a-z0-9_]*/
    table_name: /[a-z_][a-z0-9_]*/
    where_clause: "WHERE" condition
    condition: column_name op value
    op: "=" | ">" | "<" | ">=" | "<="
    value: NUMBER | "'" /[^']*/ "'"
    NUMBER: /[0-9]+(\.[0-9]+)?/
"""

if st.button("🧬 Generate from grammar"):
    from outlines.types import CFG

    grammar = ARITHMETIC_GRAMMAR if grammar_choice == "Arithmetic expressions" else SQL_GRAMMAR
    with st.spinner("Loading local model + generating on CPU…"):
        try:
            local_model = ui.get_outlines_local_model(local_model_name)
            result = local_model(user_prompt, CFG(grammar))
        except Exception as e:  # noqa: BLE001
            ui.api_error(e)
            st.stop()

    st.code(result, language="sql" if "SQL" in grammar_choice else "python")

    if grammar_choice == "Arithmetic expressions":
        try:
            ast.parse(result, mode="eval")
            st.success("✅ `ast.parse` accepted it — syntactically valid by construction.")
        except SyntaxError as e:  # pragma: no cover - should be impossible
            st.error(f"Parse failed?! {e}")
    else:
        try:
            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE t (id INTEGER, name TEXT, amount REAL)")
            conn.execute(f"EXPLAIN QUERY PLAN {result}")
            st.success("✅ SQLite's planner accepted it — valid SQL by construction.")
        except sqlite3.Error as e:  # pragma: no cover - should be impossible
            st.error(f"Parse failed?! {e}")

    with st.expander("Show the grammar"):
        st.code(grammar, language="lark")

st.info(
    "💡 The difference in one line: Instructor **asks + validates + retries**; "
    "Outlines **removes the invalid options from the model's vocabulary entirely**."
)
