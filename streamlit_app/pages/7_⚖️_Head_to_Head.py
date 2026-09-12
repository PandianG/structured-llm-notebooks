"""Page 5 — Head-to-head: raw vs Instructor vs Outlines on one input."""

import json
import sys
import time
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # allow `shared` imports

from shared import data, models, prompts, ui  # noqa: E402

import src.config as config  # noqa: E402

st.set_page_config(page_title="5 · Head-to-Head", page_icon="⚖️", layout="wide")
ui.inject_css()

st.title("⚖️ Head-to-Head: three pipelines, one input")
st.markdown(
    """
The same invoice goes through **raw prompting**, **Instructor**, and **Outlines**.
Compare what comes back: validity, shape, and latency.
"""
)

ui.render_sidebar()
model_name = config.get_openai_model()
openai_client = ui.get_openai_client()
instructor_client = ui.get_instructor("openai")
outlines_model = ui.get_outlines_model()

sample = data.load_invoices(1)[0]
text = st.text_area("Invoice text", value=sample["raw_text"], height=100)

if st.button("⚔️ Run all three", type="primary"):
    verdicts = []

    # --- Pipeline 1: raw -----------------------------------------------------
    col_raw, col_inst, col_outl = st.columns(3)

    start = time.time()
    raw_str, raw_valid_json, raw_schema_valid = None, False, False
    try:
        with st.spinner("1/3 raw prompting…"):
            resp = openai_client.chat.completions.create(
                model=model_name,
                messages=prompts.raw_extract_prompt(prompts.INVOICE_SCHEMA_HINT, text),
                temperature=0.0,
            )
        raw_str = resp.choices[0].message.content
        try:
            parsed = json.loads(raw_str)
            raw_valid_json = True
            models.Invoice.model_validate(parsed)
            raw_schema_valid = True
        except (json.JSONDecodeError, ValueError):
            pass
    except Exception as e:  # noqa: BLE001
        ui.api_error(e)
        st.stop()
    raw_time = time.time() - start

    with col_raw:
        st.subheader("1 · Raw prompting")
        if raw_str is not None:
            st.code((raw_str or "")[:600], language=None)
        st.caption(f"⏱ {raw_time:.2f}s")
        verdicts.append(
            {
                "pipeline": "Raw prompting",
                "valid JSON": "✅" if raw_valid_json else "❌",
                "schema-valid": "✅" if raw_schema_valid else "❌",
                "typed object": "❌",
                "latency (s)": round(raw_time, 2),
            }
        )

    # --- Pipeline 2: Instructor ----------------------------------------------
    start = time.time()
    inst_obj, inst_ok = None, False
    try:
        with st.spinner("2/3 Instructor…"):
            inst_obj = instructor_client.chat.completions.create(
                model=model_name,
                response_model=models.Invoice,
                messages=[{"role": "user", "content": f"Extract invoice: {text}"}],
            )
        inst_ok = True
    except Exception as e:  # noqa: BLE001
        st.warning(f"Instructor path raised: `{type(e).__name__}` (retries exhausted)")
    inst_time = time.time() - start

    with col_inst:
        st.subheader("2 · Instructor")
        if inst_ok and inst_obj:
            st.json(inst_obj.model_dump())
        st.caption(f"⏱ {inst_time:.2f}s")
        verdicts.append(
            {
                "pipeline": "Instructor",
                "valid JSON": "✅" if inst_ok else "❌",
                "schema-valid": "✅" if inst_ok else "❌",
                "typed object": "✅" if inst_ok else "❌",
                "latency (s)": round(inst_time, 2),
            }
        )

    # --- Pipeline 3: Outlines -------------------------------------------------
    start = time.time()
    outl_obj, outl_ok = None, False
    try:
        with st.spinner("3/3 Outlines…"):
            outl_str = outlines_model(f"Extract invoice: {text}", models.Invoice)
        outl_obj = models.Invoice.model_validate_json(outl_str)
        outl_ok = True
    except Exception as e:  # noqa: BLE001
        st.warning(f"Outlines path raised: `{type(e).__name__}`")
    outl_time = time.time() - start

    with col_outl:
        st.subheader("3 · Outlines")
        if outl_ok and outl_obj:
            st.json(outl_obj.model_dump())
        st.caption(f"⏱ {outl_time:.2f}s")
        verdicts.append(
            {
                "pipeline": "Outlines",
                "valid JSON": "✅" if outl_ok else "❌",
                "schema-valid": "✅" if outl_ok else "❌",
                "typed object": "✅" if outl_ok else "❌",
                "latency (s)": round(outl_time, 2),
            }
        )

    st.divider()
    st.markdown("**Verdict table**")
    st.dataframe(pd.DataFrame(verdicts), width="stretch", hide_index=True)

    st.success(
        """
**Takeaways**
- **Instructor** = validated, typed Pydantic objects with auto-retry. One API across
  OpenAI / Anthropic / local models. Best default for application code.
- **Outlines** = hard token-level guarantees (JSON, regex, grammars). No retries, no
  parse step — ideal when validity is critical or when running local models.
- **Raw prompting** = fastest to write, cheapest per call when it works, and silently
  wrong often enough to matter.
        """
    )
