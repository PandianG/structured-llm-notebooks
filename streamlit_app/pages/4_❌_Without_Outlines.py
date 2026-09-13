"""Page 3 — Without Outlines: raw constrained generation and its leaks."""

import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # allow `shared` imports

from shared import data, prompts, ui  # noqa: E402

import src.config as config  # noqa: E402

st.set_page_config(page_title="3 · Without Outlines", page_icon="❌", layout="wide")
ui.inject_css()

st.title("❌ Without Outlines: asking nicely is not a constraint")
st.markdown(
    """
Instructor *validates and retries*. Outlines does something stronger: it constrains the
**tokens the model is allowed to emit**. First, see what raw prompting does on
constraint-style tasks — formats, enums, and code.
"""
)

settings = ui.render_sidebar()
client = ui.get_openai_client()
model_name = config.get_model()

# ---------------------------------------------------------------------------
# Demo A — raw "regex" task
# ---------------------------------------------------------------------------
ui.section(
    "Demo A — “generate a phone number in the format XXX-XXXX”",
    "Ask plainly, sample several times, and check each reply against the pattern "
    r"`\d{3}-\d{4}`. How many pass?",
)

n_samples = st.slider("Samples", 3, 10, 5)
phone_pattern = re.compile(r"^\d{3}-\d{4}$")

if st.button("📞 Generate raw", type="primary"):
    outputs = []
    with st.spinner("Sampling…"):
        for _ in range(n_samples):
            try:
                resp = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": prompts.PHONE_SYSTEM},
                        {"role": "user", "content": "Go."},
                    ],
                    temperature=settings["temperature"],
                )
                raw = (resp.choices[0].message.content or "").strip()
            except Exception as e:  # noqa: BLE001
                ui.api_error(e)
                st.stop()
            outputs.append({"output": raw, "matches \\d{3}-\\d{4}": bool(phone_pattern.match(raw))})

    df = pd.DataFrame(outputs)
    st.dataframe(df, width="stretch")
    passed = df["matches \\d{3}-\\d{4}"].sum()
    st.metric("Match rate", f"{passed}/{len(df)}")
    if passed < len(df):
        st.warning(
            "Formats drift: parentheses, country codes, words, extra text. Your regex "
            "downstream now needs to handle every variant — or crash."
        )

# ---------------------------------------------------------------------------
# Demo B — raw enum task: sentiment labels
# ---------------------------------------------------------------------------
ui.section(
    "Demo B — “reply with just the label” (sentiment over real data)",
    "We classify N real reviews from `data/sentiment_data.jsonl` with a plain prompt. "
    "The contract says `positive | negative | neutral` — collect what the model "
    "*actually* says and count exact matches.",
)

if st.button("🏷️ Classify raw", type="primary"):
    rows = data.load_sentiments(settings["sample_size"])
    labels, correct = [], 0
    progress = st.progress(0, text="Classifying…")
    for i, row in enumerate(rows):
        try:
            resp = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": prompts.SENTIMENT_SYSTEM},
                    {"role": "user", "content": row["text"]},
                ],
                temperature=settings["temperature"],
            )
            label = (resp.choices[0].message.content or "").strip()
        except Exception as e:  # noqa: BLE001
            ui.api_error(e)
            st.stop()
        labels.append(label)
        correct += label.lower() == row["expected_label"]
        progress.progress((i + 1) / len(rows), text=f"{i + 1}/{len(rows)} done")

    counts = Counter(lbl.lower() for lbl in labels)
    st.bar_chart(
        pd.DataFrame({"label": list(counts), "count": list(counts.values())}).set_index("label")
    )

    canonical = sum(counts.get(k, 0) for k in ("positive", "negative", "neutral"))
    st.metric("Exact canonical-label match", f"{canonical}/{len(labels)}")
    st.metric("Also correct vs ground truth", f"{correct}/{len(labels)}")
    st.warning(
        "Non-canonical replies (capitalization, “Positive!”, extra words) all need "
        "downstream normalization — more code, more bugs."
    )
    st.session_state["raw_sentiment_adherence"] = canonical / len(labels) * 100

# ---------------------------------------------------------------------------
# Demo C — the bridge to page 4
# ---------------------------------------------------------------------------
ui.section(
    "Demo C — and the JSON problem is the same story",
    "The raw invoice benchmark on Page 1 **is** the without-Outlines story for JSON: "
    "the model is *asked* to conform to a schema but never *forced* to. Next page "
    "reruns both benchmarks with Outlines — where invalid output is impossible.",
)

if "raw_invoice_adherence" in st.session_state:
    st.info(
        f"📌 You measured **{st.session_state['raw_invoice_adherence']:.0f}%** schema-valid "
        "on the raw invoice benchmark in Page 1. See Page 4 for the Outlines numbers."
    )
if "raw_sentiment_adherence" in st.session_state:
    st.info(
        f"📌 Raw sentiment labels matched the contract "
        f"**{st.session_state['raw_sentiment_adherence']:.0f}%** of the time (Demo B above)."
    )
