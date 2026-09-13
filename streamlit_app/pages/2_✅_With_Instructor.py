"""Page 2 — With Instructor: typed extraction, validators, streaming, providers."""

import sys
import time
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # allow `shared` imports

from shared import data, models, ui  # noqa: E402

import src.config as config  # noqa: E402

st.set_page_config(page_title="2 · With Instructor", page_icon="✅", layout="wide")
ui.inject_css()

st.title("✅ With Instructor: typed, validated, streamable")
st.markdown(
    """
Same model, same task — but Instructor takes a `response_model` and guarantees the
result **validates as a Pydantic object** before your code ever sees it.
"""
)

settings = ui.render_sidebar()
model_name = config.get_model()

# ---------------------------------------------------------------------------
# Demo A — the one-line difference
# ---------------------------------------------------------------------------
ui.section(
    "Demo A — compare with Page 1",
    "Run the same extraction. The only change: `response_model=Invoice`. Instructor "
    "handles the schema prompting, parsing, validation, and retries for you.",
)

sample_invoice = data.load_invoices(1)[0]
text = st.text_area("Invoice text", value=sample_invoice["raw_text"], height=100)

if st.button("🚀 Extract with Instructor", type="primary"):
    client = ui.get_instructor()
    ui.show_code(
        "The exact code that runs",
        f"""from pydantic import BaseModel, Field
from typing import Literal

class Invoice(BaseModel):          # your schema, in Python
    invoice_number: str
    customer_name: str
    items: list[LineItem]
    subtotal: float
    tax_rate: float = Field(ge=0, le=1)
    total_amount: float
    payment_status: Literal["paid", "pending", "overdue"]

invoice = client.chat.completions.create(
    model={model_name!r},
    response_model=Invoice,        # <-- the only real difference
    messages=[{{"role": "user", "content": text}}],
)                                  # returns an Invoice, or raises after retries
""",
    )
    try:
        with st.spinner("Extracting…"):
            invoice = client.chat.completions.create(
                model=model_name,
                response_model=models.Invoice,
                messages=[{"role": "user", "content": f"Extract invoice: {text}"}],
                max_retries=config.INSTRUCTOR_MAX_RETRIES,
            )
    except Exception as e:  # noqa: BLE001
        ui.api_error(e)
        st.stop()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**The result is a typed `Invoice` object:**")
        st.json(invoice.model_dump())
        st.caption(
            f"Python type: `{type(invoice).__name__}` — access `invoice.total_amount` directly."
        )
    with c2:
        st.markdown("**Line items as a dataframe (no manual parsing):**")
        st.dataframe(pd.DataFrame([it.model_dump() for it in invoice.items]), width="stretch")

# ---------------------------------------------------------------------------
# Demo B — validators and auto-repair
# ---------------------------------------------------------------------------
ui.section(
    "Demo B — validators: Instructor retries until the data is *right*",
    "Our `Person` model demands `0 ≤ age ≤ 120` and a capitalized name. Feed it "
    "deliberately bad input and watch Instructor's retry loop fix (or reject) it.",
)

person_text = st.text_input(
    "Person text (try adversarial input)",
    value="alice, -5, lives in new york",
)

if st.button("🛠️ Extract Person"):
    client = ui.get_instructor()
    retries_seen = []
    try:
        with st.spinner("Extracting (may retry)…"):
            person = client.chat.completions.create(
                model=model_name,
                response_model=models.Person,
                messages=[{"role": "user", "content": person_text}],
                max_retries=config.INSTRUCTOR_MAX_RETRIES,
            )
    except Exception as e:  # noqa: BLE001
        st.error(
            f"Instructor exhausted its retries and raised: `{type(e).__name__}` — "
            "**the failure is loud, not silent.** That is the point."
        )
        st.stop()

    st.success(f"Got a valid `Person`: `{person.model_dump_json()}`")
    st.caption(
        f"Validation rules applied: age in [0, 120], name capitalized. "
        f"Instructor was allowed {config.INSTRUCTOR_MAX_RETRIES} retries."
    )

ui.show_code(
    "The Person model with validators",
    """class Person(BaseModel):
    name: str
    age: int = Field(ge=0, le=120)

    @field_validator("name")
    @classmethod
    def name_must_be_capitalized(cls, v: str) -> str:
        fixed = v.strip().title()
        if fixed != v:
            raise ValueError(f"name must be capitalized, got {v!r}")
        return v""",
)

# ---------------------------------------------------------------------------
# Demo C — live streaming
# ---------------------------------------------------------------------------
ui.section(
    "Demo C — streaming partial objects",
    "`create_partial()` yields progressively-complete objects. The placeholder below "
    "fills in field by field — this is how you build live-updating UIs.",
)

if st.button("📡 Stream a Person"):
    client = ui.get_instructor()

    placeholder = st.empty()
    start = time.time()
    first_field_time = None
    with st.spinner("Streaming…"):
        for partial in client.chat.completions.create_partial(
            model=model_name,
            response_model=models.Person,
            messages=[{"role": "user", "content": "Carol, 35, based in Chicago"}],
        ):
            placeholder.json(partial.model_dump())
            if partial.name and first_field_time is None:
                first_field_time = time.time() - start

    total = time.time() - start
    c1, c2 = st.columns(2)
    c1.metric("Time to first field", f"{first_field_time:.2f}s")
    c2.metric("Total time", f"{total:.2f}s")
    st.info("Users start reading data ~instantly instead of waiting for the full response.")

# ---------------------------------------------------------------------------
# Demo D — provider switcher
# ---------------------------------------------------------------------------
ui.section(
    "Demo D — same code, different provider",
    "Instructor wraps OpenAI, Anthropic, and local models behind one API. Run the same "
    "extraction on two providers and compare the structured output.",
)

provider = st.radio("Provider", ["openai", "anthropic", "gemini", "groq"], horizontal=True)
if st.button("🌐 Extract with " + provider):
    client = ui.get_instructor(provider)
    use_model = config.get_model(provider)
    try:
        with st.spinner(f"Calling {provider}…"):
            kwargs = {}
            if provider == "anthropic":
                kwargs["max_tokens"] = 1024  # Anthropic requires max_tokens
            result = client.chat.completions.create(
                model=use_model,
                response_model=models.Person,
                messages=[{"role": "user", "content": "Alice, 30, lives in New York"}],
                max_retries=config.INSTRUCTOR_MAX_RETRIES,
                **kwargs,
            )
    except Exception as e:  # noqa: BLE001
        ui.api_error(e)
        st.stop()

    st.success(f"{provider} (`{use_model}`) returned: `{result.model_dump_json()}`")
    st.caption(
        "Different company, different model, different wire protocol — identical "
        "structured result. Only the client construction changed."
    )
